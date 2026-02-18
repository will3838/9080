"""SQLite inventory storage."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    return Path("data") / "inventory.db"


def _connect() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=FULL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    return conn


def init_inventory_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory(
                user_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                count INTEGER NOT NULL,
                PRIMARY KEY(user_id, item_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                chat_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                delta INTEGER NOT NULL
            )
            """
        )
        conn.commit()


def add_item(user_id: int, item_id: int, username: str, chat_id: int, timestamp: str) -> None:
    with _connect() as conn:
        conn.execute("BEGIN")
        conn.execute(
            """
            INSERT INTO inventory(user_id, item_id, count)
            VALUES(?, ?, 1)
            ON CONFLICT(user_id, item_id) DO UPDATE SET count = count + 1
            """,
            (user_id, item_id),
        )
        conn.execute(
            """
            INSERT INTO inventory_log(timestamp, user_id, username, chat_id, item_id, delta)
            VALUES(?, ?, ?, ?, ?, 1)
            """,
            (timestamp, user_id, username, chat_id, item_id),
        )
        conn.commit()


def get_inventory_rows(user_id: int) -> list[tuple[int, int]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT item_id, count FROM inventory WHERE user_id = ? ORDER BY item_id ASC",
            (user_id,),
        ).fetchall()
    return [(int(item_id), int(count)) for item_id, count in rows]
