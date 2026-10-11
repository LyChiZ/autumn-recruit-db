# 架构说明（Architecture）

## 总体设计

`autumn-recruit-db` 采用 **本地优先（Local-first）** 的轻量架构：

```
┌────────────────────────────────────────────────────────────┐
│  入口层                                                     │
│  ├─ Streamlit UI（src/ui/app.py）  可视化操作与看板          │
│  └─ CLI（src/cli.py）              无 UI 全流程跑通          │
└──────────────┬─────────────────────────────────────────────┘
               │
┌──────────────▼─────────────────────────────────────────────┐
│  解析层 parser                                              │
│  ├─ pdf_parser.py   pdfplumber → 文本                       │
│  ├─ docx_parser.py  python-docx → 文本（含表格）             │
│  ├─ md_parser.py    标准库剥离 Markdown 标记                 │
│  └─ llm.py          OpenAI 兼容接口结构化抽取（可选，         │
│                     未配置 LLM_API_KEY 时自动回退规则解析）    │
└──────────────┬─────────────────────────────────────────────┘
               │  统一 Resume 对象（base.py）
┌──────────────▼─────────────────────────────────────────────┐
│  匹配层 matcher                                             │
│  ├─ scoring.py      技能60% + 学历20% + 城市10% + 经历10%    │
│  └─ keyword_matcher.py  批量排序 + 匹配分析文案              │
└──────────────┬─────────────────────────────────────────────┘
               │
┌──────────────▼─────────────────────────────────────────────┐
│  存储层 database（SQLite，本地文件 data/autumn_recruit.db）  │
│  ├─ schema.sql    六张表：candidate/jobs/applications/      │
│  │                interviews/offers/sources                 │
│  └─ dao.py        数据访问层（JSON 字段自动序列化）           │
└──────────────┬─────────────────────────────────────────────┘
               │
┌──────────────▼─────────────────────────────────────────────┐
│  工具层 utils                                               │
│  ├─ dates.py      DDL 解析与临期提醒                         │
│  └─ exporter.py   CSV / Markdown / Notion / Excel 四格式导出 │
└────────────────────────────────────────────────────────────┘
```

## 关键设计决策

| 决策 | 选择 | 理由 |
| --- | --- | --- |
| 技术栈 | Python + Streamlit（主推） | 零前端门槛，单文件即可交付完整面板 |
| 备选方案 | Next.js + FastAPI | 需要多用户/深度定制前端时迁移 |
| 存储 | SQLite 单文件 | 零运维、本地隐私；`DB_PATH` 环境变量可切换路径 |
| 简历解析 | 规则抽取为主 + LLM 可选 | 开箱即用不花钱；配置 `LLM_API_KEY` 后自动升级精度 |
| 岗位数据 | 本地维护 + 手动录入 | 不绑定任何第三方 API；公开数据源可通过插件式导入（见 Roadmap） |
| 隐私 | Local-first + .gitignore 隔离 | 简历与投递数据不出本机 |

## LLM 可选能力接入

1. 设置环境变量（或在 `.streamlit/secrets.toml` 中配置）：
   ```
   LLM_API_KEY=sk-xxx
   LLM_BASE_URL=https://api.openai.com/v1   # 可换任意 OpenAI 兼容网关（Ollama/vLLM/云厂商）
   LLM_MODEL=gpt-4o-mini
   ```
2. UI「简历上传与解析」页勾选「启用 LLM 结构化抽取」。
3. 未配置时静默回退规则解析，主流程不受影响。

## 目录职责

```
src/
├── parser/    简历格式解析 → 统一 Resume
├── matcher/    简历 × 岗位 打分推荐
├── database/   SQLite 建表与 DAO、示例种子
├── ui/         Streamlit 页面与组件
├── utils/      日期/导出/文件工具
└── cli.py      命令行入口（parse/match/seed/remind/export/demo）
data/
├── samples/    虚构脱敏示例（简历 + 岗位）
├── schema/     字段字典 fields.json
├── uploads/    上传临时文件（gitignore）
└── exports/    导出产物（gitignore）
tests/           pytest 单测（parser/matcher/dao）
docs/           架构与数据模型文档
.github/        CI 与 Issue/PR 模板
```
