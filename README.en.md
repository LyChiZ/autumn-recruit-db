<div align="center">

<img src="docs/images/logo.svg" width="140" alt="autumn-recruit-db logo"/>

# 🍂 autumn-recruit-db

**From one resume to an offer comparison table — your whole campus recruiting season in a local-first dashboard.**

Upload your resume and get your own **Campus Recruitment Database**: job matching, application tracking, deadline alerts, interview reviews and offer comparison.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-blue.svg)](.github/workflows/ci.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

## Why

Campus recruitment is an information war: dozens of companies × hundreds of roles × multiple channels. Spreadsheets and browser bookmarks make it easy to miss applications, interviews and deadlines. Existing tools are either too light (status tracking only) or too heavy (self-hosted DB + frontend).

**What makes autumn-recruit-db different:**

| Pain point | Our solution |
| --- | --- |
| Re-typing resume info everywhere | **Upload PDF/DOCX/MD → auto-structured** (education / skills / projects / internships) |
| Don't know which roles to apply to | **4-dimension scoring** based on resume keywords (skills / education / location / experience) |
| Applications scattered everywhere | Local SQLite + **6-state kanban** (To-Apply / Applied / Written Test / Interview / Offer / Rejected) |
| Missing deadlines | Sidebar **deadline alerts** (configurable window, default 7 days) |
| Forgetting what happened in interviews | **Interview reviews + question archive** per round |
| Hard to choose between offers | **Offer comparison table** (salary / benefits / pros / cons / decision) |
| Fear of vendor lock-in | One-click export to **CSV / Markdown / Notion / Excel** |

**Target users**: campus recruits (undergrad/master/PhD) in China's autumn & spring hiring seasons — especially those mass-applying and needing structured tracking.

---

## Quick Start (3 minutes)

> Requires Python 3.9+. Everything runs locally; your resume never leaves your machine.

```bash
git clone https://github.com/<your-username>/autumn-recruit-db.git
cd autumn-recruit-db

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Zero-config demo with fictional anonymized sample data
python src/cli.py demo

# Launch the web dashboard and upload your own resume
streamlit run src/ui/app.py
```

Open `http://localhost:8501` and follow the pages:
1. **① Resume Upload & Parse** → upload your PDF / Word / Markdown resume, preview the structured JSON
2. **② Job Matching** → use sample jobs or add your own, get 4-dimension ranked recommendations
3. **③ Application Kanban** → move cards across 6 states
4. **④ Interview Review / ⑤ Offer Compare / ⑥ Export** → full loop

---

## Features

- [x] **Resume parsing**: PDF (pdfplumber) / DOCX (python-docx) / Markdown → education, skills, projects, internships + contacts
- [x] **Job matching**: 4-dimension scoring (skills 60% + education 20% + location 10% + experience 10%) with sub-scores & fit analysis
- [x] **Application database**: structured table (company / role / JD / applied date / status / deadline), local SQLite
- [x] **Progress tracking**: 6-state kanban + per-status statistics
- [x] **Reminders & review**: deadline alerts, interview question archive, offer comparison
- [x] **Export**: CSV / Markdown / Notion template / Excel (4 sheets)
- [x] **Optional LLM extraction**: any OpenAI-compatible endpoint (Ollama / vLLM / cloud), falls back to rule-based automatically
- [ ] **Cloud sync / collaboration**: Roadmap v1.0

## Tech Stack

| Layer | Primary | Alternative |
| --- | --- | --- |
| Stack | **Python + Streamlit** (zero frontend barrier) | Next.js + FastAPI |
| Resume parsing | pdfplumber / python-docx + rules | LLM structured extraction (built-in optional) |
| Storage | SQLite (local file, switchable via `DB_PATH`) | Postgres / Supabase (cloud sync) |
| Deployment | Streamlit Cloud / local | Docker / Vercel |

## Privacy

- **Local-first**: resume, applications, interviews and offers live in a local SQLite file (`data/autumn_recruit.db`). Nothing is uploaded to the cloud.
- `.gitignore` explicitly excludes personal-data paths (`../秋招投递列表/`, `*.personal.*`, `private/`, uploads & exports).
- All sample data in this repo is **fictional and anonymized** (张三 / XX大学 / 某互联网公司).
- Optional LLM extraction only sends your resume text to the endpoint you configure.

## Roadmap

| Version | Milestone | Scope |
| --- | --- | --- |
| **v0.1** (now) | MVP | resume parsing, 4-dim matching, kanban, interview/offer records, exports, CLI, CI |
| **v0.5** | Reminders & review | email/browser deadline notifications, resume-optimization suggestions, interview question bank, Notion two-way sync |
| **v1.0** | Cloud & collaboration | Postgres/Supabase sync, shared application pools, public job-source plugins (example/replaceable), mobile support |

## Contributing

Any contribution is welcome: bugs, features, docs, design. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) first.

> **Privacy red line**: no real resumes, application records or contact info in this repo. Samples must stay fictional.

## Troubleshooting

**Q1: `python -m venv .venv` fails on macOS with `Resource deadlock avoided` / EDEADLK?**

> Cause: folders like `~/Documents` are under iCloud/Spotlight file-coordination monitoring, and bulk file operations by pip/venv can hit a macOS filesystem deadlock.
> Fix: create the virtualenv outside the project (e.g. `~/.venvs/`) and use its absolute path:

```bash
python3.13 -m venv ~/.venvs/autumn-recruit-db
source ~/.venvs/autumn-recruit-db/bin/activate
pip install -r requirements.txt
pytest -q
```

**Q2: Resume parsing returned empty / missing key fields?**

- The rule-based parser relies on common section headings (教育背景/专业技能/项目经历/实习经历, Chinese or English). For unusual layouts, fill in name & skills manually on page ①.
- Enable LLM extraction for higher accuracy: set `LLM_API_KEY` (any OpenAI-compatible endpoint), then toggle "Enable LLM extraction" on the upload page. Falls back to rule-based automatically when unconfigured.
- Supported formats: PDF / DOCX / Markdown / plain text only.

**Q3: How to store the database elsewhere (not the default `data/autumn_recruit.db`)?**

> Use the `DB_PATH` environment variable:

```bash
DB_PATH=/path/to/my-recruit.db streamlit run src/ui/app.py
# CLI: DB_PATH=/path/to/my-recruit.db python src/cli.py demo
```

## License

[MIT](LICENSE) © autumn-recruit-db contributors
