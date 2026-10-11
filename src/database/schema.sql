-- ============================================================
-- autumn-recruit-db SQLite 数据模型（v0.1）
-- 设计参考：通用化的"秋招数据库"字段体系（企业库 / 岗位清单 /
-- 投递追踪 / 面试复盘 / Offer 对比 / 信源可信度），全部字段通用化，
-- 不含任何个人数据。
-- ============================================================

-- 候选人画像：由简历解析结果写入（仅存一份最新解析）
CREATE TABLE IF NOT EXISTS candidate (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT DEFAULT '',          -- 姓名
    headline      TEXT DEFAULT '',          -- 一句话定位
    contact_email TEXT DEFAULT '',          -- 邮箱
    contact_phone TEXT DEFAULT '',          -- 电话
    education     TEXT DEFAULT '[]',        -- JSON: [{school,degree,major,period}]
    skills        TEXT DEFAULT '[]',        -- JSON: [技能关键词]
    projects      TEXT DEFAULT '[]',        -- JSON: [项目经历]
    internships   TEXT DEFAULT '[]',        -- JSON: [实习经历]
    source_format TEXT DEFAULT '',          -- pdf / docx / md / llm
    parsed_at     TEXT DEFAULT (datetime('now','localtime'))
);

-- 岗位库：来源于简历匹配推荐 / 手动录入 / 数据源导入
CREATE TABLE IF NOT EXISTS jobs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    company           TEXT NOT NULL,        -- 公司
    title             TEXT NOT NULL,        -- 岗位名称
    department        TEXT DEFAULT '',      -- 部门
    job_family        TEXT DEFAULT '',      -- 方向分类（数据/产品/运营/战略…）
    tier              TEXT DEFAULT '',      -- 公司梯队（Tier 1/2/3）
    country           TEXT DEFAULT '',      -- 国家
    city              TEXT DEFAULT '',      -- 城市
    remote            TEXT DEFAULT '',      -- 办公模式（Onsite/混合/远程）
    education_req     TEXT DEFAULT '',      -- 学历要求
    experience_req    TEXT DEFAULT '',      -- 经验要求
    jd_summary        TEXT DEFAULT '',      -- JD 摘要
    keywords          TEXT DEFAULT '[]',    -- JSON: 匹配关键词
    compensation      TEXT DEFAULT '',      -- 薪资口径+来源（示例可替换）
    wlb               TEXT DEFAULT '',      -- 工作生活平衡备注
    source_url        TEXT DEFAULT '',      -- 投递链接 / 来源链接
    application_status TEXT DEFAULT '在招', -- 招聘状态：在招/截止/待公布
    posting_date      TEXT DEFAULT '',      -- 发布日期
    deadline          TEXT DEFAULT '',      -- 截止日期（YYYY-MM-DD 或 描述）
    match_score       REAL DEFAULT 0,       -- 匹配度 0-100
    overall_score     REAL DEFAULT 0,       -- 综合评分 0-100
    sub_scores        TEXT DEFAULT '{}',    -- JSON: 分项得分
    fit_analysis      TEXT DEFAULT '',      -- 匹配分析一句话
    created_at        TEXT DEFAULT (datetime('now','localtime'))
);

-- 投递追踪：看板六态 = 待投 / 已投 / 笔试 / 面试 / Offer / 感谢信
CREATE TABLE IF NOT EXISTS applications (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id        INTEGER NOT NULL REFERENCES jobs(id),
    applied_at    TEXT DEFAULT '',          -- 投递日期 YYYY-MM-DD
    channel       TEXT DEFAULT '',          -- 投递渠道：官网/内推/邮箱/招聘平台
    referrer      TEXT DEFAULT '',          -- 内推人
    status        TEXT DEFAULT '待投'
                  CHECK (status IN ('待投','已投','笔试','面试','Offer','感谢信')),
    next_action   TEXT DEFAULT '',          -- 下一动作（如：等笔试通知）
    notes         TEXT DEFAULT '',          -- 备注
    created_at    TEXT DEFAULT (datetime('now','localtime'))
);

-- 面试追踪：一轮面试一条记录
CREATE TABLE IF NOT EXISTS interviews (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id  INTEGER NOT NULL REFERENCES applications(id),
    interview_date  TEXT DEFAULT '',        -- 面试日期 YYYY-MM-DD
    round           TEXT DEFAULT '',        -- 轮次：一面/二面/终面/HR面
    format          TEXT DEFAULT '',        -- 形式：线上/线下
    result          TEXT DEFAULT '待定'      -- 结果：通过/挂/待定
                    CHECK (result IN ('通过','挂','待定')),
    review          TEXT DEFAULT '',        -- 复盘要点
    questions       TEXT DEFAULT '[]',      -- JSON: 面试问题归档
    notes           TEXT DEFAULT '',        -- 备注
    created_at      TEXT DEFAULT (datetime('now','localtime'))
);

-- Offer 对比：每家公司一条，可横向比较
CREATE TABLE IF NOT EXISTS offers (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id   INTEGER NOT NULL REFERENCES applications(id),
    company          TEXT DEFAULT '',
    title            TEXT DEFAULT '',
    offer_date       TEXT DEFAULT '',       -- 收到日期
    base_salary      TEXT DEFAULT '',       -- 月薪 base
    total_package    TEXT DEFAULT '',       -- 年薪总包（口径+来源）
    bonus            TEXT DEFAULT '',       -- 奖金/签字费
    location         TEXT DEFAULT '',
    benefits         TEXT DEFAULT '',       -- 福利（房补/餐补/年假…）
    decision_deadline TEXT DEFAULT '',      -- 确认期限
    pros             TEXT DEFAULT '',       -- 优点
    cons             TEXT DEFAULT '',       -- 缺点
    decision         TEXT DEFAULT '待定'     -- 决策：接受/拒绝/待定
                    CHECK (decision IN ('接受','拒绝','待定')),
    created_at       TEXT DEFAULT (datetime('now','localtime'))
);

-- 信源可信度：记录每条岗位信息的来源与可信度（高/中/低/待核实）
CREATE TABLE IF NOT EXISTS sources (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id       INTEGER REFERENCES jobs(id),
    info_type    TEXT DEFAULT '',           -- 岗位/薪酬/福利/政策
    summary      TEXT DEFAULT '',           -- 信息项摘要
    source_name  TEXT DEFAULT '',           -- 来源名称
    source_url   TEXT DEFAULT '',           -- 来源 URL
    credibility  TEXT DEFAULT '待核实'
                 CHECK (credibility IN ('高','中','低','待核实')),
    created_at   TEXT DEFAULT (datetime('now','localtime'))
);

-- 常用索引
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_deadline ON jobs(deadline);
CREATE INDEX IF NOT EXISTS idx_interviews_app ON interviews(application_id);
