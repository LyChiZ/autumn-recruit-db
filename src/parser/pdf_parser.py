# -*- coding: utf-8 -*-
"""PDF 简历解析：基于 pdfplumber 抽取文本（含表格文本），再交给规则抽取器。"""

from __future__ import annotations

from .base import Resume
from .extractor import extract_from_text


def parse_pdf(file_path: str) -> Resume:
    """解析 PDF 简历文件。

    Args:
        file_path: PDF 文件路径

    Returns:
        Resume: 结构化简历对象
    """
    # 延迟导入：仅在真正解析 PDF 时引入重依赖，加快 CLI 启动
    import pdfplumber

    pages_text: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            # 同时抽取表格文本（许多简历用表格排版）
            for table in page.extract_tables() or []:
                for row in table:
                    cells = [str(c).strip() for c in row if c is not None]
                    if cells:
                        page_text += "\n" + " | ".join(cells)
            pages_text.append(page_text)

    full_text = "\n\n".join(pages_text)
    return extract_from_text(full_text, source_format="pdf")
