# -*- coding: utf-8 -*-
"""数据库 DAO 测试：建表、岗位/投递/面试/Offer 全链路 CRUD。"""

from __future__ import annotations

import pytest

from database.db import Database
from database.dao import JobDAO, ApplicationDAO, InterviewDAO, OfferDAO


@pytest.fixture()
def db():
    """内存数据库（每次测试独立）。"""
    database = Database(":memory:")
    yield database
    database.close()


def test_schema_initialized(db):
    """建表后核心表存在。"""
    tables = {r["name"] for r in db.query_all(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"candidate", "jobs", "applications", "interviews", "offers", "sources"} <= tables


def test_job_crud(db):
    """岗位：写入 → 读取 → 模糊过滤 → 删除。"""
    dao = JobDAO(db)
    jid = dao.add({
        "company": "启明云科技（示例）", "title": "商业分析师",
        "city": "上海", "job_family": "数据", "tier": "Tier 2",
        "deadline": "2026-11-30", "keywords": ["Python", "SQL"],
        "sub_scores": {"skills": 80, "education": 100},
    })
    row = dao.get(jid)
    assert row["company"] == "启明云科技（示例）"
    assert row["keywords"] == ["Python", "SQL"]  # JSON 反序列化
    assert dao.count() == 1
    assert len(dao.list(keyword="商业")) == 1
    dao.delete(jid)
    assert dao.count() == 0


def test_application_status_workflow(db):
    """投递：六态流转 + 状态统计。"""
    jdao, adao = JobDAO(db), ApplicationDAO(db)
    jid = jdao.add({"company": "示例公司", "title": "岗位A"})

    aid = adao.add(jid, status="待投", channel="官网")
    assert adao.list(status="待投")[0]["company"] == "示例公司"

    adao.update_status(aid, "面试")
    stats = adao.count_by_status()
    assert stats["面试"] == 1 and stats["待投"] == 0

    # 非法状态应报错（与 schema CHECK 一致）
    with pytest.raises(AssertionError):
        adao.update_status(aid, "未知状态")


def test_interview_and_offer_chain(db):
    """面试与 Offer：关联投递的完整链路。"""
    jdao, adao = JobDAO(db), ApplicationDAO(db)
    idao, odao = InterviewDAO(db), OfferDAO(db)

    jid = jdao.add({"company": "示例公司", "title": "岗位A"})
    aid = adao.add(jid, status="面试")

    iid = idao.add(aid, interview_date="2026-11-05", round="一面",
                   result="通过", review="SQL 需加强", questions=["如何设计 A/B 实验？"])
    records = idao.list()
    assert len(records) == 1
    assert records[0]["questions"] == ["如何设计 A/B 实验？"]

    oid = odao.add(aid, company="示例公司", title="岗位A",
                   base_salary="25K", total_package="40万/年", pros="平台大", cons="加班多")
    offers = odao.list()
    assert len(offers) == 1
    odao.update_decision(oid, "接受")
    assert odao.list()[0]["decision"] == "接受"


def test_candidate_save(db):
    """候选人：覆盖保存（永远只有最新一份）。"""
    from database.dao import CandidateDAO
    from parser.base import Resume

    cdao = CandidateDAO(db)
    r1 = Resume(name="张三", skills=["Python"], raw_text="test")
    r2 = Resume(name="李四", skills=["SQL"], raw_text="test2")
    cdao.save(r1)
    cdao.save(r2)
    profile = cdao.get()
    assert profile["name"] == "李四"
