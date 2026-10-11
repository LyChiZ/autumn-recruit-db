<div align="center">

<img src="docs/images/logo.svg" width="140" alt="autumn-recruit-db logo"/>

# 🍂 autumn-recruit-db

**你的秋招，从一份简历开始，到一张 Offer 对比表结束。**

Upload your resume → get your own **Campus Recruitment Database**: job matching, application tracking, deadline alerts, interview reviews and offer comparison — all in one local-first dashboard.

上传一份简历，自动生成专属「秋招数据库」：岗位匹配、投递追踪、DDL 提醒、面试复盘、Offer 对比，一站式本地面板。

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-blue.svg)](.github/workflows/ci.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![PRW](https://img.shields.io/badge/Private%20by%20default-✓-9DC08B)](docs/architecture.md)

</div>

---

## 为什么做这个项目（Why）

秋招是一场信息战：几十家公司 × 上百个岗位 × 多个渠道，全靠 Excel + 微信收藏夹，极易漏投、漏面、错过 DDL。现有工具要么太轻（只能记状态），要么太重（要自建数据库 + 前端）。

**autumn-recruit-db 的差异化亮点：**

| 痛点 | 本项目的解法 |
| --- | --- |
| 简历信息重复填写 | **上传 PDF/DOCX/MD 即自动结构化**（教育/技能/项目/实习） |
| 不知道投什么岗位 | 基于简历关键词的 **四维打分匹配**（技能/学历/城市/经历） |
| 投递记录散落各处 | 本地 SQLite + **六态看板**（待投/已投/笔试/面试/Offer/感谢信） |
| 错过截止日期 | 侧边栏 **DDL 临期提醒**（7 天窗口，可配置） |
| 面完就忘 | **面试复盘 + 问题归档**，每轮面试一条记录 |
| 多个 Offer 难抉择 | **Offer 横向对比表**（薪资/福利/利弊/决策） |
| 换工具怕锁死数据 | 一键导出 **CSV / Markdown / Notion / Excel** |

**目标用户**：国内秋招 / 春招的应届生（本硕博均可），尤其是海投几十家公司、需要结构化追踪的同学。

---

## 3 分钟快速开始（Quick Start）

> 需要 Python 3.9+，全程本地运行，简历与数据不出本机。

```bash
# 1. 克隆或进入项目目录
git clone https://github.com/<your-username>/autumn-recruit-db.git
cd autumn-recruit-db

# 2. 安装依赖
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. 零配置体验（载入虚构脱敏示例数据，跑通全流程）
python src/cli.py demo

# 4. 启动 Web 面板（上传你自己的简历开始使用）
streamlit run src/ui/app.py
```

浏览器自动打开 `http://localhost:8501`：

1. **① 简历上传与解析** → 上传你的 PDF / Word / Markdown 简历，查看结构化结果
2. **② 岗位匹配** → 使用示例岗位库或手动录入岗位，获得四维评分推荐
3. **③ 投递看板** → 拖动（下拉）卡片流转六态
4. **④ 面试复盘 / ⑤ Offer 对比 / ⑥ 数据导出** → 完整闭环

> 想先看效果？`python src/cli.py demo` 会用虚构数据完成「解析 → 匹配 → 入库 → 提醒 → 导出」全流程演示。

---

## Demo 截图

> 截图占位：仓库维护者可在发布前补充真实截图（`docs/images/demo.png`），
> 提交后请将本段替换为 `<img src="docs/images/demo.png" alt="Demo">`。

```
┌──────────────────────────────────────────────────────────┐
│  🍂 秋招数据库                    候选人：张三             │
│  ┌──────────────────────────────────────────────────┐    │
│  │  ①简历上传  ②岗位匹配  ③投递看板  ④面试  ⑤Offer  ⑥导出 │    │
│  └──────────────────────────────────────────────────┘    │
│  看板：待投(3)  已投(5)  笔试(2)  面试(4)  Offer(2)  感谢信(1)│
│  ⏰ 未来7天内截止 3 个岗位：启明云科技 剩 5 天 …             │
└──────────────────────────────────────────────────────────┘
```

---

## 功能特性（Features）

- [x] **简历解析**：PDF（pdfplumber）/ DOCX（python-docx）/ Markdown，抽取教育、技能、项目、实习四类结构 + 联系方式
- [x] **岗位匹配**：四维打分（技能 60% + 学历 20% + 城市 10% + 经历 10%），带分项得分与匹配分析文案
- [x] **秋招数据库**：自动生成结构化投递表（公司/岗位/JD/投递时间/状态/截止日期），SQLite 本地存储
- [x] **进度追踪**：六态看板（待投/已投/笔试/面试/Offer/感谢信）+ 状态统计
- [x] **提醒与复盘**：DDL 临期提醒（默认 7 天）、面试问题归档、Offer 对比表
- [x] **数据导出**：CSV / Markdown / Notion 模板 / Excel（四 Sheet）
- [x] **可选 LLM 抽取**：OpenAI 兼容接口（Ollama / vLLM / 云厂商均可），未配置自动回退规则解析
- [ ] **云同步 / 多人协作**：Roadmap v1.0

> 📖 详细使用教程见 [docs/usage.md](docs/usage.md)

---

## 技术选型（Tech Stack）

| 层 | 主推 | 备选 |
| --- | --- | --- |
| 技术栈 | **Python + Streamlit**（零前端门槛） | Next.js + FastAPI |
| 简历解析 | pdfplumber / python-docx + 规则抽取 | LLM 结构化抽取（已内置可选） |
| 存储 | SQLite（本地单文件，`DB_PATH` 可切换） | Postgres / Supabase（云同步） |
| 部署 | Streamlit Cloud / 本机运行 | Docker / Vercel |

---

## 项目结构（Structure）

```
autumn-recruit-db/
├── README.md / README.en.md / LICENSE / CONTRIBUTING.md / CODE_OF_CONDUCT.md
├── requirements.txt / pyproject.toml / .gitignore
├── src/
│   ├── cli.py                # 命令行入口（parse/match/seed/remind/export/demo）
│   ├── parser/               # 简历解析：pdf / docx / md / 可选 llm
│   ├── matcher/              # 岗位匹配：scoring + keyword_matcher
│   ├── database/             # SQLite：schema.sql / db / dao / sample_seed
│   ├── ui/                   # Streamlit：app.py（六页）+ components
│   └── utils/                # dates（DDL 提醒）/ exporter（四格式导出）/ io
├── data/
│   ├── samples/              # 虚构脱敏示例（sample_resume.md / jobs_sample.json）
│   └── schema/fields.json    # 字段字典
├── docs/                     # architecture.md / data-model.md / images/
├── tests/                    # pytest：parser / matcher / dao
└── .github/                  # workflows/ci.yml + Issue/PR 模板
```

---

## 隐私与数据隔离（Privacy）

本项目 **本地优先（Local-first）**：

- 简历、投递记录、面试与 Offer 数据全部保存在本机 SQLite（`data/autumn_recruit.db`），**不上传任何云端**。
- `.gitignore` 显式排除个人数据路径（`../秋招投递列表/`、`*.personal.*`、`private/`、上传与导出目录）。
- 仓库内示例数据全部为**虚构脱敏**（张三 / XX大学 / 某互联网公司）。
- 可选 LLM 抽取仅在开启时把简历文本发送到你配置的端点，请确认端点可信后使用。

---

## Roadmap

| 版本 | 里程碑 | 内容 |
| --- | --- | --- |
| **v0.1**（当前） | MVP | 简历解析、四维岗位匹配、六态看板、面试/Offer 记录、四格式导出、CLI、CI |
| **v0.5** | 提醒与复盘增强 | 邮件/浏览器 DDL 通知、简历优化建议生成、面试问题题库、Notion 双向同步 |
| **v1.0** | 云同步与协作 | Postgres/Supabase 云同步、多人共享投递池、公开岗位数据源插件（示例/可替换）、移动端适配 |

详见 [docs/roadmap 讨论](https://github.com/<your-username>/autumn-recruit-db/issues)。

---

## 贡献（Contributing）

欢迎任何形式的贡献：提 Bug、加功能、写文档、做设计。

- 提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- 隐私红线：**仓库内禁止出现真实个人简历 / 投递记录 / 联系方式**，示例一律虚构

## 常见问题（FAQ / Troubleshooting）

**Q1：macOS 上 `python -m venv .venv` 报错 `Resource deadlock avoided` / EDEADLK？**

> 原因：`~/Documents` 等目录处于 iCloud / Spotlight 文件协调监控下，pip 与 venv 的批量文件操作可能触发 macOS 文件系统死锁。
> 解决：把虚拟环境建在项目外（如 `~/.venvs/`），再通过绝对路径使用：

```bash
python3.13 -m venv ~/.venvs/autumn-recruit-db
source ~/.venvs/autumn-recruit-db/bin/activate
pip install -r requirements.txt
pytest -q
```

**Q2：简历解析结果为空 / 关键字段没抽出来？**

- 规则解析依赖常见小节标题（教育背景/专业技能/项目经历/实习经历，中英文均可）；若简历排版特殊，请手动在「① 简历上传与解析」页补全姓名与技能。
- 启用 LLM 抽取可显著提升精度：配置 `LLM_API_KEY`（OpenAI 兼容接口均可）后，在页面上勾选「启用 LLM 结构化抽取」，未配置时自动回退规则解析。
- 支持格式仅限 PDF / DOCX / Markdown / 纯文本，其他格式请先转换。

**Q3：如何把数据库放到别的位置（而非默认的 `data/autumn_recruit.db`）？**

> 通过环境变量 `DB_PATH` 指定：

```bash
DB_PATH=/path/to/my-recruit.db streamlit run src/ui/app.py
# 或命令行：DB_PATH=/path/to/my-recruit.db python src/cli.py demo
```

## License

[MIT](LICENSE) © autumn-recruit-db contributors

---

<div align="center">

**用一份简历，管理一整季秋招。** 🍂

</div>
