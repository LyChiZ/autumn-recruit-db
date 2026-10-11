# -*- coding: utf-8 -*-
"""岗位匹配器测试：打分范围、排序与分项维度。"""

from __future__ import annotations

from parser.base import Education, Resume
from matcher import match_jobs, match_job, build_sub_scores

RESUME = Resume(
    name="张三",
    headline="数据与商业分析方向",
    contact_email="zhangsan@example.com",
    skills=["Python", "SQL", "数据分析", "机器学习", "商业分析"],
    projects=["转化漏斗分析", "推荐召回实验"],
    internships=["某互联网公司 数据分析实习生"],
)
RESUME.education = [Education(school="XX大学", degree="硕士", major="计算机", period="2025-2027")]
RESUME.raw_text = "张三 数据 商业分析 Python SQL 机器学习 数据分析 转化漏斗 推荐 实习生"

JOB_DS = {
    "company": "启明云科技（示例）",
    "title": "商业分析师",
    "jd_summary": "负责经营指标体系搭建、ROI 测算与专题分析，使用 Python/SQL。",
    "keywords": ["Python", "SQL", "数据分析", "商业分析", "指标体系"],
    "education_req": "硕士及以上",
    "experience_req": "有数据分析实习优先",
    "city": "上海",
    "tier": "Tier 2",
    "job_family": "数据",
}

JOB_OPS = {
    "company": "星环网络（示例）",
    "title": "运营专员",
    "jd_summary": "负责活动策划与渠道投放。",
    "keywords": ["运营", "活动策划", "投放"],
    "education_req": "本科及以上",
    "experience_req": "无",
    "city": "广州",
    "tier": "Tier 3",
    "job_family": "运营",
}


def test_build_sub_scores_dims():
    """分项得分包含四个维度且均在 0-100。"""
    sub = build_sub_scores(RESUME, JOB_DS, preferred_cities=["上海", "杭州"])
    assert set(sub.keys()) == {"skills", "education", "location", "experience"}
    for v in sub.values():
        assert 0 <= v <= 100


def test_data_job_outranks_ops_job():
    """数据岗位应显著高于运营岗位（技能与城市双重优势）。"""
    results = match_jobs(RESUME, [JOB_DS, JOB_OPS], preferred_cities=["上海", "杭州"])
    assert results[0]["company"] == JOB_DS["company"]
    assert results[0]["overall_score"] > results[1]["overall_score"]


def test_match_score_range_and_fields():
    """单岗位匹配：匹配度在 0-100 且带分析文案。"""
    result = match_job(RESUME, JOB_DS, preferred_cities=["上海"])
    assert 0 <= result["match_score"] <= 100
    assert 0 <= result["overall_score"] <= 100
    assert result["sub_scores"]["skills"] >= 50  # 高度对口
    assert result["fit_analysis"]
