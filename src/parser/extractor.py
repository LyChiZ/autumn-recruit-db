# -*- coding: utf-8 -*-
"""基于规则的简历分段抽取器。

思路：按常见小节标题（中英文）把简历文本切成区块，
再对每个区块做针对性提取：
- 教育区块 → 学校 / 学历 / 专业 / 时间
- 技能区块 → 拆分为技能关键词列表
- 项目 / 实习区块 → 逐条要点

局限：规则解析对"自由排版"简历的召回有限，
如需更高精度可启用 llm.py 的 LLM 结构化抽取（配置后自动升级）。
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from .base import Education, Resume

# ---- 小节标题识别（中英文 + 常见变体）----
_SECTION_PATTERNS = [
    ("education", r"(教育背景|教育经历|学历|教育|EDUCATION|EDUCATIONAL)"),
    ("skills", r"(专业技能|技能清单|技能|技术栈|SKILLS|TECHNICAL SKILLS|CORE SKILLS)"),
    ("projects", r"(项目经历|项目经验|项目|PROJECTS|PROJECT EXPERIENCE)"),
    ("internships", r"(实习经历|工作经历|实习|工作经验|经历|INTERNSHIP|WORK EXPERIENCE|EXPERIENCE)"),
]

# 中英文学历关键词（用于教育区块解析）
_DEGREE_ZH = ["博士", "硕士", "本科", "学士", "大专"]
_DEGREE_EN = [r"phd", r"ph\.?d", "master", "msc", "mba", "bachelor", "bsc", "ba"]

# 姓名识别：行首 2-4 个中文字（或整行为纯英文短词）
_NAME_ZH_RE = re.compile(r"^([\u4e00-\u9fa5·]{2,4})")
_NAME_EN_RE = re.compile(r"^([A-Za-z][A-Za-z\s'\-]{1,30})$")

# 邮箱 / 电话正则
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(
    r"(\+?\d{1,3}[-\s]?)?(\(?\d{2,4}\)?[-\s]?)?\d{3,4}[-\s]?\d{4}"
)


def _split_sections(text: str) -> List[Tuple[str, str]]:
    """把全文按小节标题切成 [(section_name, content)] 列表，按出现顺序返回。"""
    # 逐行扫描，记录每行命中的小节类型
    lines = text.splitlines()
    sections: List[Tuple[str, str]] = []
    current: str = "other"      # 未命中标题的内容归入 other
    buffer: List[str] = []

    def flush() -> None:
        nonlocal buffer
        content = "\n".join(buffer).strip()
        if content:
            sections.append((current, content))
        buffer = []

    for line in lines:
        matched = None
        for name, pattern in _SECTION_PATTERNS:
            # 标题行特征：较短（<30字）且基本只含标题词
            stripped = line.strip().lstrip("#*-— ")
            if re.search(pattern, stripped, re.IGNORECASE) and len(stripped) <= 30:
                matched = name
                break
        if matched and matched != current:
            flush()
            current = matched
        else:
            buffer.append(line)
    flush()
    return sections


def _extract_education(block: str) -> List[Education]:
    """从教育区块提取教育经历条目（按段落/空行切分，逐条解析）。"""
    entries: List[Education] = []
    # 按空行或“•/-”列表项切分
    chunks = re.split(r"\n\s*\n|\n\s*[•\-·]\s*", block.strip())
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
        if not lines:
            continue
        edu = Education()
        joined = " ".join(lines)
        # 学历
        for deg in _DEGREE_ZH:
            if deg in joined:
                edu.degree = deg
                break
        if not edu.degree:
            m = re.search(r"(" + "|".join(_DEGREE_EN) + r")\b", joined, re.IGNORECASE)
            if m:
                edu.degree = m.group(1).capitalize()
        # 时间区间
        m = re.search(r"(\d{4}[./年]\s*\d{0,2}月?)\s*[-~至到]\s*(\d{4}[./年]|\S{0,8})", joined)
        if m:
            edu.period = joined[m.start():m.end()]
        # 学校：优先含“大学/学院”的行
        for ln in lines:
            if re.search(r"(大学|学院|UNIVERSITY|INSTITUTE|COLLEGE)", ln, re.IGNORECASE):
                edu.school = re.sub(r"^\s*[•\-·]\s*", "", ln).strip()
                break
        # 专业：排除已识别为学校的行后，取剩余行中最像专业的一句
        if not edu.major:
            rest = [ln for ln in lines if ln not in (edu.school, edu.period) and "大学" not in ln and "学院" not in ln]
            for ln in rest:
                if re.search(r"(专业|方向|MAJOR|专业：)", ln, re.IGNORECASE) or len(ln) <= 40:
                    edu.major = re.sub(r"^\s*(专业|方向|MAJOR)\s*[:：]?\s*", "", ln, flags=re.IGNORECASE).strip()
                    if edu.major:
                        break
        entries.append(edu)
    return entries


def _extract_skills(block: str) -> List[str]:
    """技能区块 → 关键词列表：按标点/换行拆分并去重去空。"""
    text = block.replace("\n", " ")
    parts = re.split(r"[，,、；;|/]+", text)
    skills: List[str] = []
    for p in parts:
        p = p.strip()
        if p and len(p) <= 40:  # 过滤过长句
            skills.append(p)
    # 去重且保留顺序
    seen = set()
    unique = []
    for s in skills:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


def _extract_bullets(block: str) -> List[str]:
    """项目/实习区块 → 逐条要点列表。"""
    items: List[str] = []
    for ln in block.splitlines():
        ln = ln.strip().lstrip("•·*-")
        if ln:
            items.append(ln)
    return items


def extract_from_text(text: str, source_format: str = "text") -> Resume:
    """入口：任意纯文本 → 结构化 Resume。"""
    resume = Resume(raw_text=text.strip(), source_format=source_format)

    # 1. 基本信息：姓名（行首中文名 或 纯英文短行）、邮箱、电话
    first_line = text.strip().splitlines()[0].strip() if text.strip() else ""
    m = _NAME_ZH_RE.match(first_line)
    if m:
        resume.name = m.group(1)
    else:
        m = _NAME_EN_RE.match(first_line)
        if m:
            resume.name = m.group(1).strip()
    m = _EMAIL_RE.search(text)
    if m:
        resume.contact_email = m.group(0)
    m = _PHONE_RE.search(text)
    if m:
        resume.contact_phone = m.group(0)

    # 2. 分段抽取
    for section, block in _split_sections(text):
        if section == "education":
            resume.education = _extract_education(block)
        elif section == "skills":
            resume.skills = _extract_skills(block)
        elif section == "projects":
            resume.projects = _extract_bullets(block)
        elif section == "internships":
            resume.internships = _extract_bullets(block)

    # 3. 一句话定位：取头部（姓名行之后）的前两句非空文本
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if len(lines) > 1:
        resume.headline = lines[1][:80]

    return resume
