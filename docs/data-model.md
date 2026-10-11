# 数据模型（Data Model）

SQLite 六张表（见 `src/database/schema.sql`），关系如下：

```
candidate (1) ──┐
                │
jobs (N) ── 1:N ── applications (N) ── 1:N ── interviews (N)
   │                                └──── 1:N ── offers (N)
   └── 1:N ── sources (N)   （岗位信源与可信度）
```

## 核心约定

- **看板六态**（`applications.status`，与 CHECK 约束一致）：
  `待投 → 已投 → 笔试 → 面试 → Offer / 感谢信`
- **JSON 字段**：`education / skills / projects / internships / keywords / sub_scores / questions`
  以 TEXT 存储、DAO 层自动序列化，保持表结构简单。
- **枚举约束**：`interviews.result`（通过/挂/待定）、`offers.decision`（接受/拒绝/待定）、
  `sources.credibility`（高/中/低/待核实），由 SQLite CHECK 兜底。
- **时间**：统一 `YYYY-MM-DD` 文本（宽松解析见 `utils/dates.py`），
  无法解析的截止日期（如"招满即止"）保持原文本，提醒逻辑自动跳过。

## 字段字典

完整字段含义、类型与示例见 `data/schema/fields.json`，此处列出最关键字段：

| 表 | 字段 | 含义 |
| --- | --- | --- |
| candidate | name / headline / contact_email / contact_phone | 候选人基本信息（简历解析产物） |
| candidate | education / skills / projects / internships | 四大结构化区块 |
| jobs | company / title / department / job_family / tier | 岗位身份与方向/梯队 |
| jobs | city / remote / education_req / experience_req | 地点与门槛 |
| jobs | jd_summary / keywords / compensation / wlb | JD 内容与匹配输入 |
| jobs | deadline / posting_date / application_status | 时间与招聘状态 |
| jobs | match_score / overall_score / sub_scores / fit_analysis | 匹配结果（由 matcher 写入） |
| applications | applied_at / channel / referrer / status / next_action / notes | 投递追踪 |
| interviews | interview_date / round / format / result / review / questions | 面试复盘与问题归档 |
| offers | base_salary / total_package / bonus / benefits / decision_deadline / pros / cons / decision | Offer 对比 |
| sources | info_type / summary / source_name / source_url / credibility | 信源可信度追溯 |

## 设计来源（提炼而非复制）

本项目的数据模型是从一份真实使用的个人秋招 Excel 工作簿中**通用化提炼**的：

- 企业总库 / 岗位匹配清单 → `jobs`（合并公司维度与岗位维度，Tier 与方向分类保留）
- 重点投递名单 A-B-C 分层 → `applications.status` 六态 + 手动分层备注
- 信息来源与可信度 → `sources` 表
- 简历优化建议（技能缺口/经历缺口/ATS 建议） → `interviews.review` 与 `jobs.fit_analysis` 承载
- 候选人画像（联系方式/一句话定位） → `candidate` 表

> 提炼过程仅借鉴字段设计与工作流，**不包含任何真实个人内容**；
> 示例数据全部为虚构占位（张三 / XX大学 / 某互联网公司）。
