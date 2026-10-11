# -*- coding: utf-8 -*-
"""SQLite 连接管理：负责建库、执行 schema.sql、提供统一连接入口。"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

# 默认数据库路径：项目根目录 data/autumn_recruit.db
_PROJECT_ROOT = Path(__file__).resolve().parents[2]  # autumn-recruit-db/
_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_db_path() -> str:
    """返回默认数据库文件路径（可用环境变量 DB_PATH 覆盖）。"""
    return os.getenv("DB_PATH", str(_PROJECT_ROOT / "data" / "autumn_recruit.db"))


class Database:
    """轻量 SQLite 封装：连接即建表。"""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or get_db_path()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 按列名访问
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self) -> None:
        """执行 schema.sql 建表（幂等）。"""
        schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
        self.conn.executescript(schema_sql)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ---- 通用查询工具 ----
    def query_all(self, sql: str, params: tuple = ()) -> list[dict]:
        cur = self.conn.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]

    def query_one(self, sql: str, params: tuple = ()) -> dict | None:
        cur = self.conn.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None

    def execute(self, sql: str, params: tuple = ()) -> int:
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur.lastrowid

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
