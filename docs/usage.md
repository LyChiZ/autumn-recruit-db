# 使用教程（Usage Guide）

> autumn-recruit-db 提供三种使用路径：**Web 面板（推荐）** / **命令行** / **一键演示**。
> 完整 FAQ 见 [README 常见问题](../README.md#常见问题faq--troubleshooting)。

---

## 1. 安装（Installation）

需要 Python 3.9+。macOS 用户若遇 `EDEADLK`，请把 venv 建在 `~/.venvs/` 下（见 FAQ Q1）。

```bash
git clone https://github.com/<your-username>/autumn-recruit-db.git
cd autumn-recruit-db

# 方式 A：项目内 venv（Linux / Windows / 非同步目录）
python -m venv .venv && source .venv/bin/activate
# 方式 B：macOS Documents 目录下推荐建在项目外
python3.13 -m venv ~/.venvs/autumn-recruit-db && source ~/.venvs/autumn-recruit-db/bin/activate

pip install -r requirements.txt
```

## 2. 三种使用路径

### 路径 ①：Web 面板（Streamlit，日常使用）

```bash
streamlit run src/ui/app.py
```

浏览器打开 `http://localhost:8501`，按六页导航操作：
① 简历上传与解析 → ② 岗位匹配 → ③ 投递看板 → ④ 面试复盘 → ⑤ Offer 对比 → ⑥ 数据导出。

### 路径 ②：命令行（脚本化 / 快速操作）

```bash
python src/cli.py parse data/samples/sample_resume.md   # 解析并输出结构化 JSON
python src/cli.py match data/samples/sample_resume.md   # 解析 + 岗位库打分排序
python src/cli.py seed                                   # 写入脱敏示例数据（空库时）
python src/cli.py remind --days 7                        # 打印 7 天内截止的岗位
python src/cli.py export                                 # 导出四种格式到 data/exports/
```

### 路径 ③：一键演示（体验全流程）

```bash
python src/cli.py demo
```

自动完成：写入虚构示例 → 简历匹配排序 → Top1 加入看板 → DDL 提醒 → 四格式导出。

## 3. 六态看板说明（Kanban）

| 状态 | 含义 | 典型下一动作 |
| --- | --- | --- |
| 待投 | 已匹配/录入但尚未投递 | 完善简历、走内推或官网投递 |
| 已投 | 已提交申请 | 记录渠道与内推人，等待笔试/一面 |
| 笔试 | 已收到并完成/等待笔试 | 刷题、准备行测/专业笔试 |
| 面试 | 进行中（一面/二面/终面/HR面） | 每轮结束后到「④ 面试复盘」归档 |
| Offer | 已收到录用 | 登记到「⑤ Offer 对比」做决策 |
| 感谢信 | 未通过 / 主动放弃 | 归档复盘，避免重复踩坑 |

看板卡片右下角下拉框即可移动状态；侧边栏实时显示各状态数量与 7 天内截止岗位。

## 4. 四种导出格式对照（Export）

| 格式 | 内容 | 适用场景 |
| --- | --- | --- |
| **CSV**（UTF-8 BOM） | 四大块各一份 CSV | Excel / 数据库导入、程序化处理 |
| **Markdown** | 单文件汇总文档（四节表格） | 归档、Git 仓库、快速分享 |
| **Notion 模板** | Notion 友好的 Markdown（标题/表格/Callout） | 粘贴进 Notion 建立协作看板 |
| **Excel** | 单文件四 Sheet（岗位库/投递/面试/Offer） | 发给人、本地表格存档 |

导出入口：Web 面板「⑥ 数据导出」一键导出；或 `python src/cli.py export`。
导出产物默认写入 `data/exports/`（已在 `.gitignore` 中排除，不会入库）。

## 5. 数据位置与隐私

- 数据库默认 `data/autumn_recruit.db`，可用 `DB_PATH` 环境变量切换（见 FAQ Q3）。
- 全部数据仅存本机；仓库 `.gitignore` 排除个人数据路径与导出目录。
- 示例数据均为虚构脱敏（张三 / XX大学 / 某互联网公司）。
