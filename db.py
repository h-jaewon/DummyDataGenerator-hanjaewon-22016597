"""SQLite 연결 및 테이블 생성/삽입 담당."""

import json
import sqlite3
from pathlib import Path


# 컬럼 타입 → SQLite 타입 매핑
_TYPE_MAP = {
    "autoincrement": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "random_int": "INTEGER",
    "random_element": "TEXT",
    "date_of_birth": "TEXT",
    "date_time_this_year": "TEXT",
    "sentence": "TEXT",
}

_DEFAULT_SQL_TYPE = "TEXT"


def _sql_type(col: dict) -> str:
    return _TYPE_MAP.get(col["type"], _DEFAULT_SQL_TYPE)


def ensure_table(conn: sqlite3.Connection, schema: dict) -> None:
    table = schema["table"]
    col_defs = ", ".join(
        f"{col['name']} {_sql_type(col)}" for col in schema["columns"]
    )
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({col_defs})")
    conn.commit()


def insert_rows(conn: sqlite3.Connection, table: str, rows: list[dict]) -> int:
    if not rows:
        return 0
    columns = list(rows[0].keys())
    placeholders = ", ".join("?" for _ in columns)
    col_str = ", ".join(columns)
    sql = f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})"
    data = [tuple(row[c] for c in columns) for row in rows]
    conn.executemany(sql, data)
    conn.commit()
    return len(data)


def open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
    return cur.fetchone()[0]


def preview_rows(conn: sqlite3.Connection, table: str, limit: int = 5) -> list[dict]:
    cur = conn.execute(f"SELECT * FROM {table} LIMIT {limit}")
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]
