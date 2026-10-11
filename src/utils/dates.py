# -*- coding: utf-8 -*-
"""日期工具：灵活解析日期、DDL 倒计时与临期提醒。"""

from __future__ import annotations

import datetime as dt
import re
from typing import List

_DATE_RE = re.compile(r"(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})日?")


def parse_date(value: str) -> dt.date | None:
    """宽松解析 YYYY-MM-DD / YYYY.MM.DD / YYYY年MM月DD日；无法解析返回 None。"""
    if not value:
        return None
    m = _DATE_RE.search(str(value))
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def days_left(value: str) -> int | None:
    """距截止日还剩多少天（自然日）。过期返回负数，无法解析返回 None。"""
    deadline = parse_date(value)
    if deadline is None:
        return None
    return (deadline - dt.date.today()).days


def deadline_reminders(
    jobs: List[dict], ahead_days: int = 7, include_expired: bool = False
) -> List[dict]:
    """扫描岗位库，返回临期（≤ ahead_days 天内截止）与可选的已过期岗位。

    Args:
        jobs: 岗位 dict 列表（须含 company/title/deadline）
        ahead_days: 提前提醒窗口（天）
        include_expired: 是否包含已过期岗位（默认仅临期）

    Returns:
        [{company, title, deadline, days_left}] 按剩余天数升序
    """
    today = dt.date.today()
    alerts = []
    for job in jobs:
        deadline = parse_date(job.get("deadline", ""))
        if deadline is None:
            continue  # 未注明截止日期的跳过（如"招满即止"）
        remain = (deadline - today).days
        if remain < 0 and not include_expired:
            continue
        if include_expired or remain <= ahead_days:
            alerts.append(
                {
                    "company": job.get("company", ""),
                    "title": job.get("title", ""),
                    "deadline": job.get("deadline", ""),
                    "days_left": remain,
                }
            )
    alerts.sort(key=lambda a: a["days_left"])
    return alerts
