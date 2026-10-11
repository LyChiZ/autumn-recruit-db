# Contributing / 贡献指南

感谢你愿意为 **autumn-recruit-db** 添砖加瓦！任何形式的贡献都欢迎：修 Bug、加功能、补文档、提设计、回答 Issue。

## 贡献方式（Ways to contribute）

1. **报 Bug**：使用 [Bug Report 模板](.github/ISSUE_TEMPLATE/bug_report.md)，附上复现步骤、环境信息与期望行为。
2. **提功能**：使用 [Feature Request 模板](.github/ISSUE_TEMPLATE/feature_request.md)，说明场景与价值。
3. **提 PR**：代码、文档、测试均可，见下方流程。

## 开发环境（Dev setup）

```bash
git clone https://github.com/<your-username>/autumn-recruit-db.git
cd autumn-recruit-db
python -m venv .venv && source .venv/bin/activate
pip install -e . pytest
pytest            # 运行全部测试
python src/cli.py demo   # 端到端冒烟
```

## 提 PR 流程（Pull request flow）

1. Fork 本仓库并创建特性分支：`git checkout -b feat/my-feature`
2. 修改代码（**关键函数请保留中文注释**），并补充/更新 `tests/` 中的单测
3. 本地验证：
   - `pytest` 全绿
   - 涉及 UI 的改动请用 `streamlit run src/ui/app.py` 自测
4. 提交 PR，描述改动内容与验证结果；CI 会在 push 后自动运行

## 代码规范（Code style）

- Python 3.9+，类型标注（`from __future__ import annotations` 可用）
- 中文注释解释"为什么"，英文命名保持惯例（函数/变量 snake_case，常量 UPPER_CASE）
- 新字段如需入库，同步更新 `src/database/schema.sql` 与 `data/schema/fields.json`
- 不引入重型依赖；新增依赖需在 PR 中说明理由并同步 `requirements.txt`

## ⚠️ 隐私红线（Privacy red line — 强制）

本项目由真实秋招实践提炼而来，但**仓库内绝不允许出现任何真实数据**：

- 禁止提交：真实简历、真实投递记录、联系方式、真实公司内部信息、个人画像
- 示例一律使用虚构占位：`张三 / XX大学 / 某互联网公司`
- 新示例数据放 `data/samples/`，并在 `data/samples/README.md` 中登记
- 如误提交个人数据，请在 PR 描述中第一时间说明并删除，必要时重写提交历史
- 不要移除 `.gitignore` 中的个人数据隔离规则

## 评审约定（Review notes）

- 保持 PR 小而聚焦；一个 PR 解决一个问题
- 行为变更必须带测试；文档变更必须可读
- 维护者会在 3 个工作日内响应

感谢你的贡献！🍂
