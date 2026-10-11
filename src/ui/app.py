# -*- coding: utf-8 -*-
"""Streamlit 主应用：秋招求职数据库（MVP）。

启动：streamlit run src/ui/app.py
功能页：
  1) 简历上传与解析   上传 PDF / DOCX / MD → 结构化 JSON → 存入本地 SQLite
  2) 岗位匹配         基于简历关键词对岗位库打分推荐
  3) 投递看板         待投 / 已投 / 笔试 / 面试 / Offer / 感谢信 六态看板
  4) 面试复盘         面试记录、问题归档、结果追踪
  5) Offer 对比       多 Offer 横向对比与决策
  6) 数据导出         CSV / Markdown / Notion / Excel
"""

from __future__ import annotations

import sys
from pathlib import Path

# 保证以 `streamlit run` 或 `python -m` 方式均可导入 src 下模块
_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import streamlit as st
import pandas as pd

from database.db import Database
from database.dao import CandidateDAO, JobDAO, ApplicationDAO, InterviewDAO, OfferDAO
from utils.dates import parse_date

# ---------------- 全局初始化 ----------------
st.set_page_config(
    page_title="秋招求职数据库",
    page_icon="🍂",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_resource
def get_database() -> Database:
    """数据库连接（缓存，避免每次交互重建）。"""
    return Database()

db = get_database()
candidate_dao = CandidateDAO(db)
job_dao = JobDAO(db)
app_dao = ApplicationDAO(db)
interview_dao = InterviewDAO(db)
offer_dao = OfferDAO(db)

PAGES = ["① 简历上传与解析", "② 岗位匹配", "③ 投递看板", "④ 面试复盘", "⑤ Offer 对比", "⑥ 数据导出"]

# ---------------- 侧边栏：全局状态与提醒 ----------------
with st.sidebar:
    st.title("🍂 秋招数据库")
    page = st.radio("功能导航", PAGES)

    profile = candidate_dao.get()
    if profile:
        st.caption(f"候选人：{profile['name']} · {profile['headline'][:24]}")
    else:
        st.caption("尚未上传简历，请先前往「简历上传与解析」")

    st.divider()

    from ui.components import render_stats, render_deadline_alerts
    render_stats(app_dao)
    render_deadline_alerts(job_dao.list())

    st.divider()
    st.caption("数据保存在本地 SQLite，不会上传云端。")

# ---------------- 页面一：简历上传与解析 ----------------
if page == PAGES[0]:
    st.header("📄 简历上传与解析")
    st.write(
        "上传 PDF / Word / Markdown 简历，自动抽取 **教育 / 技能 / 项目 / 实习** "
        "四类结构，并识别联系方式。可选接入 LLM 提升抽取精度（见 docs/architecture.md）。"
    )

    uploaded = st.file_uploader(
        "选择简历文件",
        type=["pdf", "docx", "md", "markdown", "txt"],
        help="支持 PDF、DOCX、Markdown、纯文本",
    )
    use_llm = st.toggle("启用 LLM 结构化抽取（需配置 LLM_API_KEY，未配置自动回退规则解析）")

    if uploaded is not None:
        # 保存上传文件到临时目录（不进入版本控制）
        tmp_dir = Path(__file__).resolve().parents[2] / "data" / "uploads"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = tmp_dir / uploaded.name
        tmp_path.write_bytes(uploaded.getvalue())

        from utils.io import detect_format
        from parser.pdf_parser import parse_pdf
        from parser.docx_parser import parse_docx
        from parser.md_parser import parse_markdown
        from parser.llm import llm_structured_extract

        try:
            fmt = detect_format(uploaded.name)
            with st.spinner("正在解析简历…"):
                resume = parse_pdf(str(tmp_path)) if fmt == "pdf" else (
                    parse_docx(str(tmp_path)) if fmt == "docx" else parse_markdown(str(tmp_path))
                )
                if use_llm:
                    llm_resume = llm_structured_extract(resume.raw_text)
                    if llm_resume is not None:
                        resume = llm_resume  # LLM 结果优先
                    else:
                        st.info("未检测到 LLM 配置，已使用规则解析结果。")

            candidate_dao.save(resume)

            st.success(f"解析完成：{resume.name or '（未识别姓名，可手动补充）'}")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("教育经历", len(resume.education))
                st.metric("技能关键词", len(resume.skills))
            with col2:
                st.metric("项目经历", len(resume.projects))
                st.metric("实习经历", len(resume.internships))

            st.subheader("结构化结果预览")
            st.json(resume.to_dict())

            st.subheader("手动修正（可选）")
            name = st.text_input("姓名", value=resume.name)
            headline = st.text_input("一句话定位", value=resume.headline)
            skills = st.text_area("技能关键词（逗号分隔）", value=", ".join(resume.skills))
            if st.button("保存修正结果"):
                resume.name = name
                resume.headline = headline
                resume.skills = [s.strip() for s in skills.replace("，", ",").split(",") if s.strip()]
                candidate_dao.save(resume)
                st.success("已更新候选人画像")
        except ValueError as e:
            st.error(str(e))

# ---------------- 页面二：岗位匹配 ----------------
elif page == PAGES[1]:
    st.header("🎯 岗位匹配")
    st.write("基于简历技能关键词与 JD 关键词，计算 **技能 / 学历 / 城市 / 经历** 四维得分并排序推荐。")

    profile = candidate_dao.get()
    if not profile:
        st.warning("请先上传简历（页面①）。也可在下方加载脱敏示例数据体验流程。")
        if st.button("载入脱敏示例数据（虚构张三 + 6 条示例岗位）"):
            from database.sample_seed import seed_sample_data
            seed_sample_data(db)
            st.success("示例数据已载入，请刷新或重新打开本页")
        st.stop()

    # 岗位来源：示例数据 or 手动录入
    mode = st.radio("岗位来源", ["使用示例岗位库", "手动录入岗位"], horizontal=True)
    jobs = []
    if mode == "使用示例岗位库":
        jobs = job_dao.list()
        if not jobs:
            st.info("岗位库为空：可先「载入示例数据」，或在下方手动录入。")
    else:
        with st.form("manual_job", clear_on_submit=True):
            st.markdown("##### 录入一个岗位（* 为必填）")
            c1, c2, c3 = st.columns(3)
            company = c1.text_input("公司 *", "")
            title = c2.text_input("岗位 *", "")
            city = c3.text_input("城市", "")
            c4, c5, c6 = st.columns(3)
            family = c4.text_input("方向（数据/产品/运营/战略…）", "")
            tier = c5.selectbox("梯队", ["", "Tier 1", "Tier 2", "Tier 3"])
            deadline = c6.text_input("截止日期（YYYY-MM-DD）", "")
            jd = st.text_area("JD 摘要 / 关键词（逗号分隔）", "")
            submitted = st.form_submit_button("加入岗位库")
            if submitted and company and title:
                keywords = [k.strip() for k in jd.replace("，", ",").split(",") if k.strip()]
                job_dao.add({
                    "company": company, "title": title, "city": city,
                    "job_family": family, "tier": tier, "deadline": deadline,
                    "jd_summary": jd, "keywords": keywords,
                    "source_url": "", "application_status": "在招",
                })
                st.success("已加入岗位库")
                jobs = job_dao.list()

    if jobs:
        # 从候选人画像构造 Resume（数据库存的是 JSON 文本）
        import json as _json
        from parser.base import Education, Resume
        resume = Resume(
            name=profile["name"], headline=profile["headline"],
            contact_email=profile["contact_email"], contact_phone=profile["contact_phone"],
            skills=_json.loads(profile["skills"] or "[]"),
            projects=_json.loads(profile["projects"] or "[]"),
            internships=_json.loads(profile["internships"] or "[]"),
        )
        resume.education = [Education(**e) for e in _json.loads(profile["education"] or "[]")]

        from matcher import match_jobs
        results = match_jobs(resume, jobs, preferred_cities=["上海", "杭州"])

        st.subheader(f"推荐结果（按综合评分排序，共 {len(results)} 条）")
        for r in results:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{r['company']}** · {r['title']}  `{r.get('job_family','')} {r.get('tier','')}`")
                    st.caption(f"{r.get('city','')} · {r.get('deadline','截止日期未注明')}")
                    st.write(r.get("fit_analysis", ""))
                with c2:
                    st.metric("综合评分", f"{r['overall_score']:.0f}", f"匹配 {r['match_score']:.0f}")
                if st.button("加入投递追踪", key=f"apply_{r['id']}"):
                    app_dao.add(r["id"], status="待投")
                    st.success("已加入看板（状态：待投）")

# ---------------- 页面三：投递看板 ----------------
elif page == PAGES[2]:
    st.header("📋 投递看板")
    st.write("六态看板：待投 → 已投 → 笔试 → 面试 → Offer / 感谢信。用卡片底部的下拉框移动卡片。")
    from ui.components import render_kanban
    render_kanban(app_dao)

# ---------------- 页面四：面试复盘 ----------------
elif page == PAGES[3]:
    st.header("🎤 面试复盘")
    apps = app_dao.list()
    if not apps:
        st.info("看板暂无投递记录，先去「岗位匹配」或手动录入投递。")
        st.stop()

    st.subheader("记录一轮新面试")
    with st.form("new_interview", clear_on_submit=True):
        options = {f"{a['company']} · {a['title']}": a["id"] for a in apps}
        sel = st.selectbox("对应投递", list(options.keys()))
        i1, i2, i3 = st.columns(3)
        date = i1.text_input("面试日期（YYYY-MM-DD）", value="")
        round_ = i2.selectbox("轮次", ["一面", "二面", "终面", "HR面", "其他"])
        fmt = i3.selectbox("形式", ["线上面试", "线下面试"])
        result = st.selectbox("结果", ["通过", "挂", "待定"])
        review = st.text_area("复盘要点（做了什么/答得如何/改进方向）")
        questions = st.text_area("面试问题归档（每行一个，自动入库）", placeholder="例如：\n1. 讲一下你的指标体系搭建思路\n2. 如何设计一个 A/B 实验")
        if st.form_submit_button("保存面试记录"):
            qlist = [q.strip() for q in questions.splitlines() if q.strip()]
            interview_dao.add(
                options[sel], interview_date=date, round=round_, format=fmt,
                result=result, review=review, questions=qlist,
            )
            st.success("已保存")

    st.subheader("面试记录总览")
    records = interview_dao.list()
    if records:
        for r in records:
            with st.container(border=True):
                st.markdown(f"**{r['company']}** · {r['title']} — {r['round']}（{r['format']}）`{r['result']}`")
                if r["interview_date"]:
                    st.caption(f"日期：{r['interview_date']}")
                if r["review"]:
                    st.write(f"📝 复盘：{r['review']}")
                if r["questions"]:
                    with st.expander(f"面试问题归档（{len(r['questions'])} 题）"):
                        for q in r["questions"]:
                            st.markdown(f"- {q}")
    else:
        st.info("暂无面试记录")

# ---------------- 页面五：Offer 对比 ----------------
elif page == PAGES[4]:
    st.header("🏆 Offer 对比")
    apps = app_dao.list()
    if not apps:
        st.info("看板暂无投递记录。")
        st.stop()

    st.subheader("登记一个 Offer")
    with st.form("new_offer", clear_on_submit=True):
        options = {f"{a['company']} · {a['title']}": a["id"] for a in apps}
        sel = st.selectbox("对应投递", list(options.keys()))
        o1, o2, o3 = st.columns(3)
        base = o1.text_input("月薪 base", placeholder="例如 25K")
        total = o2.text_input("年薪总包", placeholder="例如 40万/年（口径+来源）")
        bonus = o3.text_input("奖金/签字费", placeholder="例如 签字费 5万")
        loc = st.text_input("城市", "")
        benefits = st.text_input("福利（房补/餐补/年假…）", "")
        deadline = st.text_input("确认期限（YYYY-MM-DD）", "")
        pros = st.text_area("优点", placeholder="平台、业务、导师、晋升…")
        cons = st.text_area("缺点", placeholder="加班、通勤、稳定性…")
        if st.form_submit_button("保存 Offer"):
            offer_dao.add(
                options[sel], company=sel.split(" · ")[0], title=sel.split(" · ")[1],
                base_salary=base, total_package=total, bonus=bonus, location=loc,
                benefits=benefits, decision_deadline=deadline, pros=pros, cons=cons,
            )
            st.success("已保存")

    st.subheader("Offer 横向对比")
    offers = offer_dao.list()
    if offers:
        df = pd.DataFrame([
            {
                "公司": o["company"], "岗位": o["title"], "收到日期": o["offer_date"],
                "月薪": o["base_salary"], "总包": o["total_package"], "奖金": o["bonus"],
                "城市": o["location"], "福利": o["benefits"], "确认期限": o["decision_deadline"],
                "优点": o["pros"], "缺点": o["cons"], "决策": o["decision"],
            }
            for o in offers
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
        # 决策操作
        for o in offers:
            cols = st.columns([3, 1, 1])
            cols[0].caption(f"{o['company']} · {o['title']}")
            new_decision = cols[1].selectbox(
                "决策", ["待定", "接受", "拒绝"], index=["待定", "接受", "拒绝"].index(o["decision"]),
                key=f"offer_decision_{o['id']}", label_visibility="collapsed",
            )
            if new_decision != o["decision"]:
                offer_dao.update_decision(o["id"], new_decision)
                st.rerun()
    else:
        st.info("暂无 Offer 记录")

# ---------------- 页面六：数据导出 ----------------
elif page == PAGES[5]:
    st.header("📤 数据导出")
    st.write("把岗位库 / 投递追踪 / 面试记录 / Offer 对比导出为多种格式，方便迁移到 Excel、Notion 或归档。")
    sections = {
        "jobs": job_dao.list(),
        "applications": app_dao.list(),
        "interviews": interview_dao.list(),
        "offers": offer_dao.list(),
    }
    from ui.components import render_export_buttons
    render_export_buttons(sections)
