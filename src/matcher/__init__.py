# -*- coding: utf-8 -*-
"""岗位匹配模块：基于简历关键词与 JD 的相似度打分，输出岗位推荐与分项得分。

打分维度（总分 0-100）：
- 技能匹配 60%：简历技能词命中 JD 的比例 + JD 关键词命中简历全文的比例
- 学历匹配 20%：简历最高学历 vs 岗位学历要求
- 城市匹配 10%：候选人偏好城市 vs 岗位城市
- 经历匹配 10%：简历实习/项目条数 vs 岗位经验要求
"""

from .keyword_matcher import match_jobs, match_job
from .scoring import build_sub_scores, overall_score

__all__ = ["match_jobs", "match_job", "build_sub_scores", "overall_score"]
