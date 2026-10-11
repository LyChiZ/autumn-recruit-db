# -*- coding: utf-8 -*-
"""数据结构：所有解析器输出的统一简历模型（与存储层解耦）。"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import List


@dataclass
class Education:
    """教育经历条目。"""

    school: str = ""      # 学校
    degree: str = ""      # 学历（本科/硕士/博士）
    major: str = ""       # 专业
    period: str = ""      # 起止时间，如 "2023.09 - 2025.06"


@dataclass
class Resume:
    """统一简历模型：任何格式解析后都归一化为本结构。"""

    # ---- 基本信息 ----
    name: str = ""                        # 姓名
    headline: str = ""                    # 一句话定位（求职意向/亮点摘要）
    contact_email: str = ""               # 邮箱
    contact_phone: str = ""               # 电话

    # ---- 结构化经历 ----
    education: List[Education] = field(default_factory=list)  # 教育经历
    skills: List[str] = field(default_factory=list)           # 技能关键词（用于岗位匹配）
    projects: List[str] = field(default_factory=list)         # 项目经历（逐条）
    internships: List[str] = field(default_factory=list)      # 实习/工作经历（逐条）

    # ---- 元信息 ----
    raw_text: str = ""          # 原始全文（供关键词匹配兜底）
    source_format: str = ""     # 来源格式：pdf / docx / md / text

    # ---------- 便捷方法 ----------
    def to_dict(self) -> dict:
        """转为 dict（可 JSON 序列化）。"""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """转为格式化 JSON 字符串（保证中文不转义）。"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def full_text_lower(self) -> str:
        """小写全文，供关键词匹配使用。"""
        return self.raw_text.lower()
