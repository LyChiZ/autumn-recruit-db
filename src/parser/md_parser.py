# -*- coding: utf-8 -*-
"""Markdown 简历解析：剥离 Markdown 标记（标题#/列表-等）后按纯文本交给规则抽取器。"""

from __future__ import annotations

import re

from .base import Resume
from .extractor import extract_from_text


def parse_markdown(file_path: str) -> Resume:
    """解析 .md / .markdown / .txt 简历文件。

    Args:
        file_path: 文本类简历文件路径

    Returns:
        Resume: 结构化简历对象
    """
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    # 剥离 Markdown 标记：标题符、列表符、加粗/行内代码、链接
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", raw)          # 图片
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)      # 链接 → 保留文字
    text = re.sub(r"`([^`]*)`", r"\1", text)                  # 行内代码
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)            # 加粗
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)  # 标题标记

    return extract_from_text(text, source_format="md")
