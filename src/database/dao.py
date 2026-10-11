# -*- coding: utf-8 -*-
"""DAO 数据访问层：候选人与岗位的增删查改。

JSON 字段（education/skills/projects/internships/keywords/sub_scores）
统一以 TEXT 存取，读写时自动 json 序列化/反序列化。
"""

from __future__ import annotations

import json
from typing import List, Optional

from .db import Database


def _dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _loads(text: str, default):
    if not text:
        return default
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


class CandidateDAO:
    """候选人画像读写（单行表：永远只有最新一份解析结果）。"""

    def __init__(self, db: Database):
        self.db = db

    def save(self, resume) -> int:
        """把 Resume 对象写入 candidate 表（先清空旧记录再插入）。"""
        self.db.conn.execute("DELETE FROM candidate")
        sql = """INSERT INTO candidate
                 (name, headline, contact_email, contact_phone,
                  education, skills, projects, internships, source_format)
                 VALUES (?,?,?,?,?,?,?,?,?)"""
        rid = self.db.execute(
            sql,
            (
                resume.name,
                resume.headline,
                resume.contact_email,
                resume.contact_phone,
                _dumps([e.__dict__ for e in resume.education]),
                _dumps(resume.skills),
                _dumps(resume.projects),
                _dumps(resume.internships),
                resume.source_format,
            ),
        )
        return rid

    def get(self) -> Optional[dict]:
        """返回最新候选人（无则 None）。"""
        return self.db.query_one("SELECT * FROM candidate ORDER BY id DESC LIMIT 1")

    def has_profile(self) -> bool:
        return self.get() is not None


class JobDAO:
    """岗位库读写。"""

    def __init__(self, db: Database):
        self.db = db

    def add(self, job: dict) -> int:
        sql = """INSERT INTO jobs
                 (company, title, department, job_family, tier, country, city,
                  remote, education_req, experience_req, jd_summary, keywords,
                  compensation, wlb, source_url, application_status,
                  posting_date, deadline, match_score, overall_score,
                  sub_scores, fit_analysis)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        return self.db.execute(
            sql,
            (
                job.get("company", ""),
                job.get("title", ""),
                job.get("department", ""),
                job.get("job_family", ""),
                job.get("tier", ""),
                job.get("country", ""),
                job.get("city", ""),
                job.get("remote", ""),
                job.get("education_req", ""),
                job.get("experience_req", ""),
                job.get("jd_summary", ""),
                _dumps(job.get("keywords", [])),
                job.get("compensation", ""),
                job.get("wlb", ""),
                job.get("source_url", ""),
                job.get("application_status", "在招"),
                job.get("posting_date", ""),
                job.get("deadline", ""),
                job.get("match_score", 0),
                job.get("overall_score", 0),
                _dumps(job.get("sub_scores", {})),
                job.get("fit_analysis", ""),
            ),
        )

    def add_many(self, jobs: List[dict]) -> int:
        """批量写入，返回条数。"""
        n = 0
        for job in jobs:
            self.add(job)
            n += 1
        return n

    def list(self, keyword: str = "") -> List[dict]:
        """岗位列表；keyword 非空时按公司/岗位名模糊过滤。"""
        sql = "SELECT * FROM jobs"
        params: tuple = ()
        if keyword:
            sql += " WHERE company LIKE ? OR title LIKE ?"
            params = (f"%{keyword}%", f"%{keyword}%")
        sql += " ORDER BY overall_score DESC, id"
        rows = self.db.query_all(sql, params)
        for r in rows:
            r["keywords"] = _loads(r.pop("keywords", ""), [])
            r["sub_scores"] = _loads(r.pop("sub_scores", ""), {})
        return rows

    def get(self, job_id: int) -> Optional[dict]:
        row = self.db.query_one("SELECT * FROM jobs WHERE id=?", (job_id,))
        if row:
            row["keywords"] = _loads(row.pop("keywords", ""), [])
            row["sub_scores"] = _loads(row.pop("sub_scores", ""), {})
        return row

    def delete(self, job_id: int) -> None:
        self.db.conn.execute("DELETE FROM jobs WHERE id=?", (job_id,))
        self.db.conn.commit()

    def count(self) -> int:
        row = self.db.query_one("SELECT COUNT(*) AS n FROM jobs")
        return row["n"] if row else 0


class ApplicationDAO:
    """投递追踪（看板六态）读写。"""

    STATUSES = ("待投", "已投", "笔试", "面试", "Offer", "感谢信")

    def __init__(self, db: Database):
        self.db = db

    def add(self, job_id: int, **kwargs) -> int:
        sql = """INSERT INTO applications
                 (job_id, applied_at, channel, referrer, status, next_action, notes)
                 VALUES (?,?,?,?,?,?,?)"""
        return self.db.execute(
            sql,
            (
                job_id,
                kwargs.get("applied_at", ""),
                kwargs.get("channel", ""),
                kwargs.get("referrer", ""),
                kwargs.get("status", "待投"),
                kwargs.get("next_action", ""),
                kwargs.get("notes", ""),
            ),
        )

    def list(self, status: str = "") -> List[dict]:
        """投递列表；status 非空时按状态过滤。附带岗位信息（JOIN）。"""
        sql = """SELECT a.*, j.company, j.title, j.city, j.deadline
                 FROM applications a JOIN jobs j ON a.job_id = j.id"""
        params: tuple = ()
        if status:
            sql += " WHERE a.status = ?"
            params = (status,)
        sql += " ORDER BY a.id DESC"
        return self.db.query_all(sql, params)

    def update_status(self, app_id: int, status: str) -> None:
        """看板拖拽/选择更新状态。"""
        assert status in self.STATUSES, f"非法状态: {status}"
        self.db.conn.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
        self.db.conn.commit()

    def update(self, app_id: int, **kwargs) -> None:
        """按需更新字段（白名单）。"""
        allowed = {"applied_at", "channel", "referrer", "status", "next_action", "notes"}
        fields = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if not fields:
            return
        sets = ", ".join(f"{k}=?" for k in fields)
        self.db.conn.execute(
            f"UPDATE applications SET {sets} WHERE id=?", (*fields.values(), app_id)
        )
        self.db.conn.commit()

    def delete(self, app_id: int) -> None:
        self.db.conn.execute("DELETE FROM applications WHERE id=?", (app_id,))
        self.db.conn.commit()

    def count_by_status(self) -> dict:
        """各状态数量统计（看板角标 + 侧边栏）。"""
        rows = self.db.query_all(
            "SELECT status, COUNT(*) AS n FROM applications GROUP BY status"
        )
        counter = {s: 0 for s in self.STATUSES}
        for r in rows:
            counter[r["status"]] = r["n"]
        return counter


class InterviewDAO:
    """面试追踪读写。"""

    def __init__(self, db: Database):
        self.db = db

    def add(self, application_id: int, **kwargs) -> int:
        sql = """INSERT INTO interviews
                 (application_id, interview_date, round, format, result,
                  review, questions, notes)
                 VALUES (?,?,?,?,?,?,?,?)"""
        return self.db.execute(
            sql,
            (
                application_id,
                kwargs.get("interview_date", ""),
                kwargs.get("round", ""),
                kwargs.get("format", ""),
                kwargs.get("result", "待定"),
                kwargs.get("review", ""),
                _dumps(kwargs.get("questions", [])),
                kwargs.get("notes", ""),
            ),
        )

    def list(self, application_id: int | None = None) -> List[dict]:
        sql = """SELECT i.*, j.company, j.title
                 FROM interviews i
                 JOIN applications a ON i.application_id = a.id
                 JOIN jobs j ON a.job_id = j.id"""
        params: tuple = ()
        if application_id is not None:
            sql += " WHERE i.application_id = ?"
            params = (application_id,)
        sql += " ORDER BY i.interview_date DESC, i.id DESC"
        rows = self.db.query_all(sql, params)
        for r in rows:
            r["questions"] = _loads(r.pop("questions", ""), [])
        return rows

    def delete(self, interview_id: int) -> None:
        self.db.conn.execute("DELETE FROM interviews WHERE id=?", (interview_id,))
        self.db.conn.commit()


class OfferDAO:
    """Offer 对比读写。"""

    def __init__(self, db: Database):
        self.db = db

    def add(self, application_id: int, **kwargs) -> int:
        sql = """INSERT INTO offers
                 (application_id, company, title, offer_date, base_salary,
                  total_package, bonus, location, benefits, decision_deadline,
                  pros, cons, decision)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        return self.db.execute(
            sql,
            (
                application_id,
                kwargs.get("company", ""),
                kwargs.get("title", ""),
                kwargs.get("offer_date", ""),
                kwargs.get("base_salary", ""),
                kwargs.get("total_package", ""),
                kwargs.get("bonus", ""),
                kwargs.get("location", ""),
                kwargs.get("benefits", ""),
                kwargs.get("decision_deadline", ""),
                kwargs.get("pros", ""),
                kwargs.get("cons", ""),
                kwargs.get("decision", "待定"),
            ),
        )

    def list(self) -> List[dict]:
        sql = """SELECT o.*, j.company AS job_company, j.title AS job_title
                 FROM offers o
                 LEFT JOIN applications a ON o.application_id = a.id
                 LEFT JOIN jobs j ON a.job_id = j.id
                 ORDER BY o.id DESC"""
        return self.db.query_all(sql)

    def update_decision(self, offer_id: int, decision: str) -> None:
        assert decision in ("接受", "拒绝", "待定")
        self.db.conn.execute(
            "UPDATE offers SET decision=? WHERE id=?", (decision, offer_id)
        )
        self.db.conn.commit()

    def delete(self, offer_id: int) -> None:
        self.db.conn.execute("DELETE FROM offers WHERE id=?", (offer_id,))
        self.db.conn.commit()
