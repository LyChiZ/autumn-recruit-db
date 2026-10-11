# -*- coding: utf-8 -*-
"""多格式导出：CSV / Markdown / Notion 模板 / Excel。

导出内容覆盖四大块：岗位库、投递追踪、面试记录、Offer 对比。
所有导出文件写入 data/exports/（已在 .gitignore 中排除）。
"""

from __future__ import annotations

import csv
import datetime
from pathlib import Path
from typing import Dict, List

# ---- 字段展示顺序（中文表头，对应通用化数据模型）----
JOB_COLUMNS = [
    ("company", "公司"), ("title", "岗位"), ("department", "部门"),
    ("job_family", "方向"), ("tier", "梯队"), ("city", "城市"),
    ("remote", "办公模式"), ("education_req", "学历要求"),
    ("deadline", "截止日期"), ("match_score", "匹配度"),
    ("overall_score", "综合评分"), ("fit_analysis", "匹配分析"),
    ("source_url", "投递链接"),
]
APP_COLUMNS = [
    ("company", "公司"), ("title", "岗位"), ("applied_at", "投递日期"),
    ("channel", "渠道"), ("referrer", "内推人"), ("status", "状态"),
    ("next_action", "下一动作"), ("notes", "备注"), ("deadline", "截止日期"),
]
INTERVIEW_COLUMNS = [
    ("interview_date", "面试日期"), ("company", "公司"), ("title", "岗位"),
    ("round", "轮次"), ("format", "形式"), ("result", "结果"),
    ("review", "复盘要点"), ("notes", "备注"),
]
OFFER_COLUMNS = [
    ("company", "公司"), ("title", "岗位"), ("offer_date", "收到日期"),
    ("base_salary", "月薪"), ("total_package", "总包"), ("bonus", "奖金"),
    ("location", "城市"), ("benefits", "福利"), ("decision_deadline", "确认期限"),
    ("pros", "优点"), ("cons", "缺点"), ("decision", "决策"),
]

_EXPORT_DIR = Path(__file__).resolve().parents[2] / "data" / "exports"


def _ensure_dir() -> Path:
    _EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    return _EXPORT_DIR


def _pick(row: dict, col: str) -> str:
    """取列值，None → 空串。"""
    v = row.get(col)
    return "" if v is None else str(v)


# ---------- CSV ----------
def export_csv(rows: List[dict], columns: List[tuple], name: str) -> str:
    """导出 CSV（UTF-8 BOM，Excel 可直接打开不乱码），返回文件路径。"""
    path = _ensure_dir() / f"{name}.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([zh for _, zh in columns])
        for row in rows:
            writer.writerow([_pick(row, key) for key, _ in columns])
    return str(path)


# ---------- Markdown ----------
def _md_table(rows: List[dict], columns: List[tuple]) -> str:
    headers = [zh for _, zh in columns]
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join([" --- "] * len(headers)) + "|"]
    for row in rows:
        cells = [_pick(row, key).replace("|", "\\|") for key, _ in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def export_markdown(
    sections: Dict[str, List[dict]], name: str = "autumn_recruit_export"
) -> str:
    """导出 Markdown 汇总文档（四大块分节），返回文件路径。"""
    path = _ensure_dir() / f"{name}.md"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = ["# 秋招数据库导出", "", f"> 生成时间：{now}", ""]
    blocks = [
        ("## 一、岗位库", JOB_COLUMNS, sections.get("jobs", [])),
        ("## 二、投递追踪", APP_COLUMNS, sections.get("applications", [])),
        ("## 三、面试记录", INTERVIEW_COLUMNS, sections.get("interviews", [])),
        ("## 四、Offer 对比", OFFER_COLUMNS, sections.get("offers", [])),
    ]
    for title, cols, rows in blocks:
        lines.append(title)
        lines.append("")
        if rows:
            lines.append(_md_table(rows, cols))
        else:
            lines.append("（暂无数据）")
        lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    return str(path)


# ---------- Notion 模板 ----------
def export_notion(
    sections: Dict[str, List[dict]], name: str = "notion_template"
) -> str:
    """导出 Notion 导入友好的 Markdown（含 Callout/标题/Toggle 语法），返回路径。"""
    path = _ensure_dir() / f"{name}.md"
    lines = [
        "# 🍂 秋招数据库（Notion 模板）",
        "",
        "> 本模板由 autumn-recruit-db 生成，可直接粘贴进 Notion 或导入。",
        "",
    ]
    for title, cols, rows in [
        ("## 📋 岗位库", JOB_COLUMNS, sections.get("jobs", [])),
        ("## 📮 投递追踪", APP_COLUMNS, sections.get("applications", [])),
        ("## 🎤 面试记录", INTERVIEW_COLUMNS, sections.get("interviews", [])),
        ("## 🏆 Offer 对比", OFFER_COLUMNS, sections.get("offers", [])),
    ]:
        lines.append(title)
        lines.append("")
        if rows:
            lines.append(_md_table(rows, cols))
        else:
            lines.append("（暂无数据）")
        lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    return str(path)


# ---------- Excel ----------
def export_excel(
    sections: Dict[str, List[dict]], name: str = "autumn_recruit_db"
) -> str:
    """导出多 Sheet Excel（openpyxl 引擎），返回文件路径。"""
    import pandas as pd

    path = _ensure_dir() / f"{name}.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        specs = [
            ("岗位库", JOB_COLUMNS, sections.get("jobs", [])),
            ("投递追踪", APP_COLUMNS, sections.get("applications", [])),
            ("面试记录", INTERVIEW_COLUMNS, sections.get("interviews", [])),
            ("Offer对比", OFFER_COLUMNS, sections.get("offers", [])),
        ]
        for sheet, cols, rows in specs:
            df = pd.DataFrame(
                [{zh: _pick(r, key) for key, zh in cols} for r in rows]
            )
            df.to_excel(writer, sheet_name=sheet, index=False)
    return str(path)
