# -*- coding: utf-8 -*-
"""文件读写工具。"""

from __future__ import annotations

from pathlib import Path

# 常见简历扩展名 → 解析器类型
SUPPORTED_SUFFIX = {".pdf", ".docx", ".md", ".markdown", ".txt"}


def read_text_file(path: str) -> str:
    """按 UTF-8 读取文本文件（容错替换非法字节）。"""
    return Path(path).read_text(encoding="utf-8", errors="replace")


def save_text_file(path: str, content: str) -> str:
    """写入 UTF-8 文本文件，返回路径。"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")
    return path


def detect_format(filename: str) -> str:
    """按扩展名识别简历格式：pdf / docx / md / text；未知格式抛 ValueError。"""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".docx":
        return "docx"
    if suffix in (".md", ".markdown", ".txt"):
        return "md"
    raise ValueError(f"暂不支持的简历格式: {suffix}（支持 pdf / docx / md / txt）")
