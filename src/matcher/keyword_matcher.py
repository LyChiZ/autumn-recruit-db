# -*- coding: utf-8 -*-
"""关键词匹配入口：把一批岗位 dict 与简历比对，返回带评分的排序列表。"""

from __future__ import annotations

from typing import Dict, List

from parser.base import Resume

from .scoring import build_sub_scores, overall_score


def match_job(
    resume: Resume,
    job: dict,
    preferred_cities: List[str] | None = None,
) -> Dict[str, object]:
    """单岗位 × 简历 匹配，返回岗位副本 + 匹配结果（不修改原 dict）。"""
    sub = build_sub_scores(resume, job, preferred_cities)
    result = dict(job)  # 拷贝，避免污染输入数据
    result["match_score"] = round(
        0.6 * sub["skills"] + 0.2 * sub["education"]
        + 0.1 * sub["location"] + 0.1 * sub["experience"],
        1,
    )
    result["overall_score"] = overall_score(sub, str(job.get("tier", "")))
    result["sub_scores"] = sub
    result["fit_analysis"] = _fit_analysis(resume, job, sub)
    return result


def match_jobs(
    resume: Resume,
    jobs: List[dict],
    preferred_cities: List[str] | None = None,
    top_n: int | None = None,
) -> List[Dict[str, object]]:
    """批量岗位匹配：按综合得分降序返回（可截断 top_n）。"""
    scored = [match_job(resume, job, preferred_cities) for job in jobs]
    scored.sort(key=lambda j: j["overall_score"], reverse=True)
    if top_n:
        return scored[:top_n]
    return scored


def _fit_analysis(resume: Resume, job: dict, sub: Dict[str, float]) -> str:
    """生成一句话匹配分析（中文），供推荐列表直接展示。"""
    reasons = []
    if sub["skills"] >= 70:
        reasons.append("技能高度对口")
    elif sub["skills"] >= 45:
        reasons.append("技能部分对口")
    if sub["education"] >= 90:
        reasons.append("学历满足要求")
    if sub["location"] >= 90:
        reasons.append("城市匹配偏好")
    if not reasons:
        reasons.append("需补充相关技能/经历")
    return "；".join(reasons) + f"（技能{sub['skills']:.0f}/学历{sub['education']:.0f}/城市{sub['location']:.0f}/经历{sub['experience']:.0f}）"
