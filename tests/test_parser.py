# -*- coding: utf-8 -*-
"""简历解析器测试：覆盖 Markdown 与 DOCX 两种格式的规则抽取。"""

from __future__ import annotations

from parser.md_parser import parse_markdown
from parser.docx_parser import parse_docx
from parser.extractor import extract_from_text

SAMPLE_MD = """# 张三 — 数据与商业分析方向（2027 届应届）

XX大学计算机硕士在读，主攻数据分析方向。

zhangsan@example.com ｜ 138-0000-0000

## 教育背景

- XX大学 计算机科学与技术 硕士 2025.09 - 2027.06
- XX理工大学 信息管理 本科 2021.09 - 2025.06

## 专业技能

Python, SQL, 数据分析, 机器学习, A/B测试, Tableau

## 项目经历

- 校园二手交易平台数据分析：搭建转化漏斗
- 商品推荐召回实验：点击率提升 12%

## 实习经历

- 某互联网公司 数据分析实习生：经营日报自动化
- 某咨询公司 商业分析实习生：行业研究
"""


def test_extract_from_text_basic():
    """基础字段：姓名 / 邮箱 / 电话 / 定位。

    说明：extract_from_text 面向纯文本输入；Markdown 标记（如 #）由
    md_parser 先行剥离，这里模拟其行为。
    """
    plain = SAMPLE_MD.replace("# ", "", 1)  # 剥离首个标题标记
    resume = extract_from_text(plain, source_format="md")
    assert resume.name == "张三"
    assert resume.contact_email == "zhangsan@example.com"
    assert resume.contact_phone == "138-0000-0000"
    assert "数据" in resume.headline


def test_extract_sections():
    """四大区块：教育 / 技能 / 项目 / 实习。"""
    resume = extract_from_text(SAMPLE_MD, source_format="md")
    assert len(resume.education) >= 2
    assert resume.education[0].degree == "硕士"
    assert "Python" in resume.skills
    assert len(resume.projects) == 2
    assert len(resume.internships) == 2


def test_parse_markdown_file(tmp_path):
    """Markdown 文件解析（剥离标记后字段仍正确）。"""
    md_path = tmp_path / "resume.md"
    md_path.write_text(SAMPLE_MD, encoding="utf-8")
    resume = parse_markdown(str(md_path))
    assert resume.name == "张三"
    assert resume.source_format == "md"
    assert "SQL" in resume.skills


def test_parse_docx_file(tmp_path):
    """DOCX 文件解析（python-docx 构造临时文件）。"""
    import docx

    doc = docx.Document()
    doc.add_paragraph("李四 — 产品方向（2027 届应届）")
    doc.add_paragraph("lisi@example.com")
    doc.add_heading("教育背景", level=1)
    doc.add_paragraph("XX大学 产品设计 本科 2022.09 - 2026.06")
    doc.add_heading("专业技能", level=1)
    doc.add_paragraph("产品, 数据分析, Axure, 用户研究")

    docx_path = tmp_path / "resume.docx"
    doc.save(str(docx_path))

    resume = parse_docx(str(docx_path))
    assert resume.name == "李四"
    assert resume.contact_email == "lisi@example.com"
    assert "产品" in resume.skills
    assert resume.source_format == "docx"
