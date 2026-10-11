# -*- coding: utf-8 -*-
"""脱敏示例种子数据。

⚠️ 隐私声明：本文件全部为虚构示例（公司名、岗位、人名为虚构），
仅用于演示与测试，与任何真实组织或个人无关。仓库内禁止出现真实数据。
"""

from __future__ import annotations

from typing import List

from .db import Database
from .dao import ApplicationDAO, CandidateDAO, JobDAO

# 虚构候选人（脱敏样本）
SAMPLE_RESUME = {
    "name": "张三",
    "headline": "XX大学计算机硕士在读，主攻数据分析与商业分析方向",
    "contact_email": "zhangsan@example.com",
    "contact_phone": "138-0000-0000",
    "education": [
        {"school": "XX大学", "degree": "硕士", "major": "计算机科学与技术", "period": "2025.09 - 2027.06"},
        {"school": "XX理工大学", "degree": "本科", "major": "信息管理", "period": "2021.09 - 2025.06"},
    ],
    "skills": ["Python", "SQL", "数据分析", "机器学习", "商业分析", "指标体系",
               "A/B测试", "Tableau", "Excel", "用户增长", "ROI分析"],
    "projects": [
        "校园二手交易平台数据分析：搭建转化漏斗与用户留存指标体系",
        "商品推荐召回实验：基于用户行为序列的 TopN 推荐，AUC 提升 4%",
    ],
    "internships": [
        "某互联网公司 数据分析实习生：负责经营日报自动化与补贴 ROI 复盘",
        "某咨询公司 商业分析实习生：参与行业研究、竞对对标与案头分析",
    ],
    "source_format": "sample",
}

# 虚构岗位库（六条，覆盖不同方向，供匹配演示）
SAMPLE_JOBS: List[dict] = [
    {
        "company": "启明云科技（示例）",
        "title": "商业分析师（2027 届校招）",
        "department": "商业分析部",
        "job_family": "数据",
        "tier": "Tier 2",
        "country": "中国",
        "city": "上海",
        "remote": "混合办公",
        "education_req": "硕士及以上",
        "experience_req": "2027 届应届，有数据分析/商业分析实习优先",
        "jd_summary": "负责经营指标体系搭建、补贴 ROI 测算与业务专题分析，支撑管理决策。",
        "keywords": ["Python", "SQL", "数据分析", "商业分析", "指标体系", "ROI"],
        "compensation": "约 30-45 万/年（示例估算）",
        "wlb": "3.0 星，约 10:00-20:00",
        "source_url": "https://example.com/campus/ba",
        "application_status": "在招",
        "posting_date": "2026-09-10",
        "deadline": "2026-11-30",
    },
    {
        "company": "数衡科技（示例）",
        "title": "数据分析师（机器学习方向）",
        "department": "数据科学组",
        "job_family": "数据",
        "tier": "Tier 2",
        "country": "中国",
        "city": "杭州",
        "remote": "Onsite",
        "education_req": "本科及以上",
        "experience_req": "有机器学习项目经验优先",
        "jd_summary": "参与用户增长实验设计、特征工程与模型上线，建设自动化报表。",
        "keywords": ["Python", "机器学习", "A/B测试", "用户增长", "数据分析", "SQL"],
        "compensation": "约 28-40 万/年（示例估算）",
        "wlb": "3.5 星，约 10:00-19:30",
        "source_url": "https://example.com/campus/ds",
        "application_status": "在招",
        "posting_date": "2026-09-15",
        "deadline": "2026-12-15",
    },
    {
        "company": "蓝屿网络（示例）",
        "title": "产品经理（数据产品方向）",
        "department": "数据产品部",
        "job_family": "产品",
        "tier": "Tier 3",
        "country": "中国",
        "city": "北京",
        "remote": "Onsite",
        "education_req": "本科及以上",
        "experience_req": "有产品实习经验优先",
        "jd_summary": "负责 BI 数据产品的需求梳理、原型设计与迭代，联动数仓与算法团队。",
        "keywords": ["数据分析", "Tableau", "Excel", "产品", "指标体系"],
        "compensation": "约 25-35 万/年（示例估算）",
        "wlb": "3.0 星，约 10:00-20:30",
        "source_url": "https://example.com/campus/pm",
        "application_status": "在招",
        "posting_date": "2026-09-20",
        "deadline": "2026-12-10",
    },
    {
        "company": "北辰咨询（示例）",
        "title": "战略咨询顾问（校招）",
        "department": "战略咨询部",
        "job_family": "战略",
        "tier": "Tier 1",
        "country": "中国",
        "city": "上海",
        "remote": "混合办公",
        "education_req": "硕士及以上",
        "experience_req": "有咨询/行研实习经历优先",
        "jd_summary": "参与行业研究与战略项目，负责案头分析、专家访谈与报告撰写。",
        "keywords": ["商业分析", "咨询", "行业研究", "PPT", "Excel"],
        "compensation": "约 35-50 万/年（示例估算）",
        "wlb": "2.5 星，约 10:00-21:30，项目期加班",
        "source_url": "https://example.com/campus/consulting",
        "application_status": "在招",
        "posting_date": "2026-09-08",
        "deadline": "2026-10-31",
    },
    {
        "company": "微澜金科（示例）",
        "title": "风控数据分析师（校招）",
        "department": "风控模型组",
        "job_family": "数据",
        "tier": "Tier 2",
        "country": "中国",
        "city": "深圳",
        "remote": "Onsite",
        "education_req": "硕士及以上",
        "experience_req": "2027 届应届",
        "jd_summary": "负责风控特征开发、策略回测与指标监控，撰写分析报告。",
        "keywords": ["Python", "SQL", "机器学习", "数据分析", "风控"],
        "compensation": "约 30-45 万/年（示例估算）",
        "wlb": "3.0 星，约 10:00-20:00",
        "source_url": "https://example.com/campus/risk",
        "application_status": "在招",
        "posting_date": "2026-09-12",
        "deadline": "2026-11-20",
    },
    {
        "company": "星环网络（示例）",
        "title": "运营专员（用户增长方向）",
        "department": "用户运营部",
        "job_family": "运营",
        "tier": "Tier 3",
        "country": "中国",
        "city": "广州",
        "remote": "Onsite",
        "education_req": "本科及以上",
        "experience_req": "有运营实习经验优先",
        "jd_summary": "负责活动策划、渠道投放与转化数据复盘，优化拉新-留存链路。",
        "keywords": ["用户增长", "数据分析", "Excel", "运营"],
        "compensation": "约 20-30 万/年（示例估算）",
        "wlb": "3.0 星，约 10:00-19:30",
        "source_url": "https://example.com/campus/ops",
        "application_status": "在招",
        "posting_date": "2026-09-18",
        "deadline": "2026-12-01",
    },
]


def seed_sample_data(db: Database) -> dict:
    """写入脱敏示例数据（候选人 + 岗位库），返回写入统计。"""
    cdao, jdao = CandidateDAO(db), JobDAO(db)

    # 候选人：构造轻量 Resume 对象
    from parser.base import Education, Resume

    resume = Resume(**{k: SAMPLE_RESUME[k] for k in
                       ("name", "headline", "contact_email", "contact_phone",
                        "skills", "projects", "internships", "source_format")})
    resume.education = [Education(**e) for e in SAMPLE_RESUME["education"]]
    cdao.save(resume)

    # 岗位库：仅在空库时写入，避免重复
    job_count = jdao.count()
    if job_count == 0:
        job_count = jdao.add_many(SAMPLE_JOBS)

    return {"candidate": 1, "jobs": job_count}
