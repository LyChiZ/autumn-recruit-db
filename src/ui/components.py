# -*- coding: utf-8 -*-
"""Streamlit 可复用组件：统计卡片 / 投递看板 / DDL 提醒 / 导出按钮。"""

from __future__ import annotations

import streamlit as st

from database.dao import ApplicationDAO
from utils.dates import deadline_reminders

# 看板六态（与 schema.sql 中的 CHECK 约束保持一致）
KANBAN_STATUSES = ["待投", "已投", "笔试", "面试", "Offer", "感谢信"]


def render_stats(app_dao: ApplicationDAO) -> None:
    """侧边栏：各状态数量统计（六列指标卡）。"""
    counter = app_dao.count_by_status()
    cols = st.columns(6)
    for col, status in zip(cols, KANBAN_STATUSES):
        col.metric(status, counter[status])


def render_deadline_alerts(jobs: list[dict], ahead_days: int = 7) -> None:
    """侧边栏：临期截止提醒（7 天内到期的高亮显示）。"""
    alerts = deadline_reminders(jobs, ahead_days=ahead_days)
    if not alerts:
        st.sidebar.info("近期无临期岗位 ✓")
        return
    st.sidebar.warning(f"⏰ 未来 {ahead_days} 天内截止 {len(alerts)} 个岗位")
    for a in alerts:
        tone = "🔴" if a["days_left"] <= 2 else "🟡"
        st.sidebar.markdown(
            f"{tone} **{a['company']}** · {a['title']} "
            f"（剩 {a['days_left']} 天，{a['deadline']}）"
        )


def render_kanban(app_dao: ApplicationDAO) -> None:
    """投递看板：六列布局，每列一个岗位卡片 + 状态下拉（移动看板卡片）。

    交互：卡片右下角用 selectbox 修改状态，即实现"拖动"效果。
    """
    apps = app_dao.list()
    columns = st.columns(6)

    for col, status in zip(columns, KANBAN_STATUSES):
        with col:
            st.subheader(f"{status} ({sum(1 for a in apps if a['status'] == status)})")
            for app in apps:
                if app["status"] != status:
                    continue
                with st.container(border=True):
                    st.markdown(f"**{app['company']}**")
                    st.caption(f"{app['title']} · {app.get('city', '')}")
                    if app.get("applied_at"):
                        st.caption(f"投递：{app['applied_at']}")
                    new_status = st.selectbox(
                        "状态",
                        KANBAN_STATUSES,
                        index=KANBAN_STATUSES.index(status),
                        key=f"kanban_{app['id']}",
                        label_visibility="collapsed",
                    )
                    if new_status != status:
                        app_dao.update_status(app["id"], new_status)
                        st.rerun()


def render_export_buttons(sections: dict) -> None:
    """导出按钮组：CSV / Markdown / Notion 模板 / Excel，一次性导出四大块。"""
    from utils.exporter import (
        export_csv,
        export_excel,
        export_markdown,
        export_notion,
        APP_COLUMNS,
        INTERVIEW_COLUMNS,
        JOB_COLUMNS,
        OFFER_COLUMNS,
    )

    st.divider()
    st.subheader("📤 数据导出")
    if st.button("一键导出全部（CSV + Markdown + Notion + Excel）"):
        files = [
            export_csv(sections.get("jobs", []), JOB_COLUMNS, "jobs"),
            export_csv(sections.get("applications", []), APP_COLUMNS, "applications"),
            export_csv(sections.get("interviews", []), INTERVIEW_COLUMNS, "interviews"),
            export_csv(sections.get("offers", []), OFFER_COLUMNS, "offers"),
            export_markdown(sections),
            export_notion(sections),
            export_excel(sections),
        ]
        st.success("已导出到 data/exports/ 目录：" )
        for f in files:
            st.code(f, language="text")
