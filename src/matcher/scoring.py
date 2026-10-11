# -*- coding: utf-8 -*-
"""分项得分计算：技能 / 学历 / 城市 / 经历 四个维度，各返回 0-100 分。"""

from __future__ import annotations

from typing import Dict, List

from parser.base import Resume


def _skill_score(resume: Resume, job: dict) -> float:
    """技能匹配分（0-100）：
    50% 简历技能词命中 JD 的比例；50% 岗位关键词命中简历全文的比例。"""
    jd_text = " ".join(
        str(job.get(k, "")) for k in ("jd_summary", "title", "department")
    ).lower()
    resume_text = resume.full_text_lower()

    # 简历侧：技能词在 JD 中出现的比例
    skill_hits = 0
    for skill in resume.skills:
        if skill and skill.lower() in jd_text:
            skill_hits += 1
    skill_ratio = skill_hits / len(resume.skills) if resume.skills else 0.0

    # 岗位侧：JD 自带关键词在简历中出现的比例
    job_keywords = [str(k).lower() for k in (job.get("keywords") or [])]
    if job_keywords:
        job_hits = sum(1 for k in job_keywords if k and k in resume_text)
        job_ratio = job_hits / len(job_keywords)
    else:
        job_ratio = 0.5  # 未提供关键词时取中性分，避免惩罚

    return round(100 * (0.5 * skill_ratio + 0.5 * job_ratio), 1)


def _education_score(resume: Resume, job: dict) -> float:
    """学历匹配分（0-100）：比对最高学历与岗位要求。"""
    req = str(job.get("education_req", "") or "")
    if not req:
        return 80.0  # 无明确要求 → 中性偏乐观

    # 简历最高学历等级
    levels = {"博士": 4, "硕士": 3, "本科": 2, "学士": 2, "大专": 1}
    resume_level = 0
    for edu in resume.education:
        for kw, lv in levels.items():
            if kw in (edu.degree or "") and lv > resume_level:
                resume_level = lv
    # 中文简历可能未写学历学位词，从全文兜底
    if resume_level == 0:
        for kw, lv in levels.items():
            if kw in resume.raw_text:
                resume_level = lv
                break

    # 岗位要求的等级
    req_level = 0
    for kw, lv in levels.items():
        if kw in req:
            req_level = max(req_level, lv)

    if req_level == 0:
        return 80.0
    if resume_level == 0:
        return 60.0  # 简历未披露学历 → 保守分
    if resume_level >= req_level:
        return 100.0
    return 55.0  # 学历不达标


def _location_score(resume: Resume, job: dict, preferred_cities: List[str]) -> float:
    """城市匹配分（0-100）：岗位城市与候选人偏好城市是否重合。"""
    job_city = str(job.get("city", "") or "")
    if not job_city:
        return 70.0  # 未注明城市 → 中性
    if not preferred_cities:
        return 80.0  # 未设置偏好 → 不惩罚
    job_city_lower = job_city.lower()
    for pref in preferred_cities:
        if pref.lower() in job_city_lower or job_city_lower in pref.lower():
            return 100.0
    return 40.0


def _experience_score(resume: Resume, job: dict) -> float:
    """经历匹配分（0-100）：岗位是否要求实习/经验，简历是否有对应条目。"""
    req = str(job.get("experience_req", "") or "").lower()
    has_experience = len(resume.internships) + len(resume.projects) > 0
    requires_exp = any(kw in req for kw in ("实习", "经验", "intern", "experience"))
    if requires_exp:
        return 100.0 if has_experience else 40.0
    return 80.0  # 校招多数岗位不硬性要求经验


def build_sub_scores(
    resume: Resume, job: dict, preferred_cities: List[str] | None = None
) -> Dict[str, float]:
    """计算四个分项得分，返回 dict（供 UI 展示与归档）。"""
    preferred_cities = preferred_cities or []
    return {
        "skills": _skill_score(resume, job),
        "education": _education_score(resume, job),
        "location": _location_score(resume, job, preferred_cities),
        "experience": _experience_score(resume, job),
    }


def overall_score(sub_scores: Dict[str, float], tier: str = "") -> float:
    """综合得分 = 技能60% + 学历20% + 城市10% + 经历10% + 公司梯队加成（上限100）。"""
    base = (
        sub_scores["skills"] * 0.6
        + sub_scores["education"] * 0.2
        + sub_scores["location"] * 0.1
        + sub_scores["experience"] * 0.1
    )
    tier_bonus = {"Tier 1": 5.0, "Tier 2": 3.0, "Tier 3": 0.0}.get(tier, 0.0)
    return round(min(100.0, base + tier_bonus), 1)
