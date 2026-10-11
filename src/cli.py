#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""命令行入口：不开 UI 也能跑通全流程。

用法（在项目根目录）：
    python src/cli.py demo                 # 全流程演示：示例简历 → 匹配 → 建库 → 导出
    python src/cli.py parse <简历文件>      # 解析简历并打印结构化 JSON
    python src/cli.py match <简历文件>      # 解析 + 对岗位库打分排序
    python src/cli.py seed                  # 写入脱敏示例数据（空库时）
    python src/cli.py remind                # 打印 7 天内截止的岗位
    python src/cli.py export               # 导出 CSV/Markdown/Notion/Excel 到 data/exports/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 保证从项目根目录运行时可导入 src 下模块
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from database.db import Database
from database.dao import CandidateDAO, JobDAO, ApplicationDAO, InterviewDAO, OfferDAO
from database.sample_seed import seed_sample_data
from utils.dates import deadline_reminders
from utils.io import detect_format
from utils.exporter import (
    export_csv, export_markdown, export_notion, export_excel,
    APP_COLUMNS, INTERVIEW_COLUMNS, JOB_COLUMNS, OFFER_COLUMNS,
)
from parser.pdf_parser import parse_pdf
from parser.docx_parser import parse_docx
from parser.md_parser import parse_markdown
from parser.llm import is_llm_configured, llm_structured_extract
from matcher import match_jobs


def _parse_resume(path: str):
    """按扩展名分发解析器，可选 LLM 升级（未配置自动回退）。"""
    fmt = detect_format(path)
    if fmt == "pdf":
        resume = parse_pdf(path)
    elif fmt == "docx":
        resume = parse_docx(path)
    else:
        resume = parse_markdown(path)
    if is_llm_configured():
        llm_resume = llm_structured_extract(resume.raw_text)
        if llm_resume is not None:
            resume = llm_resume
    return resume


def cmd_parse(args) -> int:
    resume = _parse_resume(args.file)
    print(resume.to_json())
    return 0


def cmd_match(args) -> int:
    resume = _parse_resume(args.file)
    db = Database()
    job_dao = JobDAO(db)
    jobs = job_dao.list()
    if not jobs:
        print("岗位库为空：请先执行 `python src/cli.py seed` 载入示例岗位。")
        return 1
    results = match_jobs(resume, jobs, preferred_cities=args.cities or ["上海", "杭州"])
    print(f"候选人：{resume.name}（技能 {len(resume.skills)} 个）\n")
    for r in results:
        print(
            f"  {r['overall_score']:5.1f}  {r['company']:<16} {r['title']}"
            f"  [{r.get('job_family','')}/{r.get('tier','')}]  {r.get('city','')}"
        )
        print(f"       匹配分析：{r.get('fit_analysis','')}")
    print(f"\n共匹配 {len(results)} 条。")
    return 0


def cmd_seed(args) -> int:
    db = Database()
    stats = seed_sample_data(db)
    print(f"示例数据已写入：候选人 {stats['candidate']} 份，岗位 {stats['jobs']} 条（空库时写入）。")
    return 0


def cmd_remind(args) -> int:
    db = Database()
    alerts = deadline_reminders(JobDAO(db).list(), ahead_days=args.days, include_expired=args.expired)
    if not alerts:
        print("近期无临期岗位。")
        return 0
    for a in alerts:
        flag = "已过期" if a["days_left"] < 0 else f"剩 {a['days_left']} 天"
        print(f"  {flag:<8} {a['company']:<16} {a['title']}  截止 {a['deadline']}")
    return 0


def cmd_export(args) -> int:
    db = Database()
    job_dao, app_dao = JobDAO(db), ApplicationDAO(db)
    interview_dao, offer_dao = InterviewDAO(db), OfferDAO(db)
    sections = {
        "jobs": job_dao.list(),
        "applications": app_dao.list(),
        "interviews": interview_dao.list(),
        "offers": offer_dao.list(),
    }
    files = [
        export_csv(sections["jobs"], JOB_COLUMNS, "jobs"),
        export_csv(sections["applications"], APP_COLUMNS, "applications"),
        export_csv(sections["interviews"], INTERVIEW_COLUMNS, "interviews"),
        export_csv(sections["offers"], OFFER_COLUMNS, "offers"),
        export_markdown(sections),
        export_notion(sections),
        export_excel(sections),
    ]
    for f in files:
        print("已导出:", f)
    return 0


def cmd_demo(args) -> int:
    """端到端演示：种子 → 示例简历匹配 → 建一条投递 → 提醒 → 导出。"""
    db = Database()
    seed_sample_data(db)
    print("✓ 已载入脱敏示例数据（虚构候选人张三 + 6 条虚构岗位）")

    # 从种子候选人构造 Resume（与 UI 共用逻辑）
    from parser.base import Education, Resume
    import json as _json

    profile = CandidateDAO(db).get()
    resume = Resume(
        name=profile["name"], headline=profile["headline"],
        contact_email=profile["contact_email"], contact_phone=profile["contact_phone"],
        skills=_json.loads(profile["skills"] or "[]"),
        projects=_json.loads(profile["projects"] or "[]"),
        internships=_json.loads(profile["internships"] or "[]"),
    )
    resume.education = [Education(**e) for e in _json.loads(profile["education"] or "[]")]

    job_dao, app_dao = JobDAO(db), ApplicationDAO(db)
    results = match_jobs(resume, job_dao.list(), preferred_cities=["上海", "杭州"])
    print("\n推荐 Top3：")
    for r in results[:3]:
        print(f"  {r['overall_score']:5.1f}  {r['company']} · {r['title']}  （{r.get('fit_analysis','')}）")

    # 把第一名加入看板（状态：待投）
    top = results[0]
    app_dao.add(top["id"], status="待投", next_action="准备简历投递")
    print(f"\n✓ 已把 Top1（{top['company']} · {top['title']}）加入看板，状态：待投")

    # DDL 提醒
    alerts = deadline_reminders(job_dao.list(), ahead_days=7)
    if alerts:
        print("\n⏰ 7 天内截止提醒：")
        for a in alerts[:3]:
            print(f"  {a['company']} · {a['title']} 剩 {a['days_left']} 天（{a['deadline']}）")

    # 导出
    cmd_export(args)
    print("\n✅ demo 完成。启动 UI：streamlit run src/ui/app.py")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="秋招求职数据库命令行工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p_parse = sub.add_parser("parse", help="解析简历并输出结构化 JSON")
    p_parse.add_argument("file")
    p_parse.set_defaults(func=cmd_parse)

    p_match = sub.add_parser("match", help="解析简历并对岗位库打分")
    p_match.add_argument("file")
    p_match.add_argument("--cities", nargs="*", default=[], help="偏好城市列表")
    p_match.set_defaults(func=cmd_match)

    sub.add_parser("seed", help="写入脱敏示例数据").set_defaults(func=cmd_seed)

    p_remind = sub.add_parser("remind", help="打印临期截止岗位")
    p_remind.add_argument("--days", type=int, default=7)
    p_remind.add_argument("--expired", action="store_true", help="同时展示已过期")
    p_remind.set_defaults(func=cmd_remind)

    sub.add_parser("export", help="导出 CSV/Markdown/Notion/Excel").set_defaults(func=cmd_export)
    sub.add_parser("demo", help="端到端演示").set_defaults(func=cmd_demo)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
