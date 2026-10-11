# -*- coding: utf-8 -*-
"""可选 LLM 结构化抽取（OpenAI 兼容接口）。

设计原则：
- 不绑定任何特定厂商，只要实现 OpenAI Chat Completions 协议即可接入
  （本地 Ollama / vLLM / 各家云模型均可）。
- 通过环境变量配置：LLM_API_KEY / LLM_BASE_URL / LLM_MODEL。
- 未配置时自动回退到规则解析（extractor），保证开箱即用、零成本。
"""

from __future__ import annotations

import json
import os
from typing import Optional

from .base import Resume

_ENV_KEY = "LLM_API_KEY"
_ENV_BASE = "LLM_BASE_URL"
_ENV_MODEL = "LLM_MODEL"

# 默认兼容 OpenAI 的公共网关（可在 .env / secrets 中覆盖）
_DEFAULT_BASE_URL = "https://api.openai.com/v1"
_DEFAULT_MODEL = "gpt-4o-mini"

_SYSTEM_PROMPT = """你是一名资深 HR 简历解析器。请把简历文本抽取为严格 JSON，字段：
{
  "name": "姓名",
  "headline": "一句话定位/求职意向，不超过40字",
  "contact_email": "邮箱",
  "contact_phone": "电话",
  "education": [{"school": "学校", "degree": "学历", "major": "专业", "period": "起止时间"}],
  "skills": ["技能关键词列表"],
  "projects": ["项目经历，每条一行"],
  "internships": ["实习/工作经历，每条一行"]
}
只输出 JSON，不要输出任何解释文字。"""


def is_llm_configured() -> bool:
    """是否已配置 LLM（配置了 API Key 即视为可用）。"""
    return bool(os.getenv(_ENV_KEY, "").strip())


def _chat_completion(system_prompt: str, user_prompt: str) -> str:
    """调用 OpenAI 兼容 Chat Completions 接口（简单同步实现）。"""
    import requests

    base_url = os.getenv(_ENV_BASE, _DEFAULT_BASE_URL).rstrip("/")
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv(_ENV_KEY)}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": os.getenv(_ENV_MODEL, _DEFAULT_MODEL),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def llm_structured_extract(text: str) -> Optional[Resume]:
    """用 LLM 抽取简历；失败或未配置时返回 None（由调用方回退规则解析）。"""
    if not is_llm_configured():
        return None
    try:
        content = _chat_completion(_SYSTEM_PROMPT, text[:6000])
        data = json.loads(content)
        resume = Resume(raw_text=text, source_format="llm")
        resume.name = data.get("name", "")
        resume.headline = data.get("headline", "")
        resume.contact_email = data.get("contact_email", "")
        resume.contact_phone = data.get("contact_phone", "")
        resume.skills = data.get("skills", []) or []
        resume.projects = data.get("projects", []) or []
        resume.internships = data.get("internships", []) or []
        from .base import Education

        resume.education = [Education(**e) for e in (data.get("education", []) or [])]
        return resume
    except Exception:  # LLM 服务不可用时不阻塞主流程
        return None
