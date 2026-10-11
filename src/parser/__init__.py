# -*- coding: utf-8 -*-
"""简历解析模块：支持 PDF / DOCX / Markdown 三种格式，输出统一结构化的 Resume 对象。

模块组成：
- base.py        数据结构定义（Resume / Education）
- extractor.py   基于规则的分段抽取（教育/技能/项目/实习 + 联系方式）
- pdf_parser.py  PDF 解析（pdfplumber）
- docx_parser.py Word 解析（python-docx）
- md_parser.py   Markdown 解析（标准库）
- llm.py         可选 LLM 结构化抽取（OpenAI 兼容接口，未配置时自动回退规则解析）
"""

from .base import Resume, Education
from .extractor import extract_from_text
from .pdf_parser import parse_pdf
from .docx_parser import parse_docx
from .md_parser import parse_markdown
from .llm import llm_structured_extract, is_llm_configured

__all__ = [
    "Resume",
    "Education",
    "extract_from_text",
    "parse_pdf",
    "parse_docx",
    "parse_markdown",
    "llm_structured_extract",
    "is_llm_configured",
]
