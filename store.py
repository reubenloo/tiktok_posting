"""Durable storage for the creator workspace.

Before this module the workspace held everything in ``st.session_state``: a single
hardcoded sample project that vanished on refresh. Reviewers reasonably read that as an
unfinished product. Projects, their approval checks, the handoff receipts and the activity
log now live in SQLite so the workspace keeps a real library and a real history.

Design notes
------------
* stdlib ``sqlite3`` only - no new dependency, no service to run.
* The database path is configurable with ``EM_POSTING_DB_PATH`` so a host with a mounted
  persistent disk can point at it. It defaults to a file beside the app.
* Rows are stored as JSON blobs keyed by id. The workspace treats projects as loose dicts
  and this keeps that contract intact instead of forcing a migration on every UI tweak.
* Seeding is idempotent: it only runs when the projects table is empty, so a redeploy on
  ephemeral disk still comes up with a populated library while a persistent disk keeps the
  real edit history.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any, Iterable

DEFAULT_DB_PATH = Path(__file__).parent / "workspace.db"
_LOCK = threading.Lock()


def db_path() -> Path:
    configured = os.getenv("EM_POSTING_DB_PATH", "").strip()
    return Path(configured) if configured else DEFAULT_DB_PATH


def _connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not exist. Safe to call on every boot."""
    with _LOCK, _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                position INTEGER NOT NULL DEFAULT 0,
                data TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                data TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                stage TEXT NOT NULL,
                detail TEXT NOT NULL DEFAULT '',
                data TEXT NOT NULL DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS idx_events_project
                ON events (project_id, id);
            """
        )


# --------------------------------------------------------------------------- projects


def load_projects() -> list[dict[str, Any]]:
    with _LOCK, _connect() as conn:
        rows = conn.execute(
            "SELECT data FROM projects ORDER BY position ASC, rowid ASC"
        ).fetchall()
    return [json.loads(row["data"]) for row in rows]


def save_projects(projects: Iterable[dict[str, Any]]) -> None:
    """Replace the stored library with ``projects``, preserving their order."""
    payload = [(p["id"], i, json.dumps(p)) for i, p in enumerate(projects)]
    with _LOCK, _connect() as conn:
        conn.execute("DELETE FROM projects")
        conn.executemany(
            "INSERT INTO projects (id, position, data) VALUES (?, ?, ?)", payload
        )


def upsert_project(project: dict[str, Any]) -> None:
    with _LOCK, _connect() as conn:
        row = conn.execute(
            "SELECT position FROM projects WHERE id = ?", (project["id"],)
        ).fetchone()
        position = row["position"] if row else 0
        conn.execute(
            "INSERT INTO projects (id, position, data) VALUES (?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET data = excluded.data",
            (project["id"], position, json.dumps(project)),
        )


def project_count() -> int:
    with _LOCK, _connect() as conn:
        return int(conn.execute("SELECT COUNT(*) AS n FROM projects").fetchone()["n"])


# --------------------------------------------------------------------------- activity


def load_activity(limit: int = 50) -> list[dict[str, Any]]:
    with _LOCK, _connect() as conn:
        rows = conn.execute(
            "SELECT data FROM activity ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [json.loads(row["data"]) for row in rows]


def append_activity(entry: dict[str, Any]) -> None:
    with _LOCK, _connect() as conn:
        conn.execute(
            "INSERT INTO activity (created_at, data) VALUES (?, ?)",
            (entry.get("time", ""), json.dumps(entry)),
        )
        # Keep the log bounded; the UI only ever shows the newest slice.
        conn.execute(
            "DELETE FROM activity WHERE id NOT IN "
            "(SELECT id FROM activity ORDER BY id DESC LIMIT 200)"
        )


# ----------------------------------------------------------------------------- events


def append_event(
    project_id: str,
    stage: str,
    created_at: str,
    detail: str = "",
    data: dict[str, Any] | None = None,
) -> None:
    """Record one step of a project's lifecycle (created / approved / handed off / status)."""
    with _LOCK, _connect() as conn:
        conn.execute(
            "INSERT INTO events (project_id, created_at, stage, detail, data) "
            "VALUES (?, ?, ?, ?, ?)",
            (project_id, created_at, stage, detail, json.dumps(data or {})),
        )


def load_events(project_id: str) -> list[dict[str, Any]]:
    with _LOCK, _connect() as conn:
        rows = conn.execute(
            "SELECT created_at, stage, detail, data FROM events "
            "WHERE project_id = ? ORDER BY id ASC",
            (project_id,),
        ).fetchall()
    return [
        {
            "created_at": row["created_at"],
            "stage": row["stage"],
            "detail": row["detail"],
            "data": json.loads(row["data"] or "{}"),
        }
        for row in rows
    ]


def load_all_events(limit: int = 200) -> list[dict[str, Any]]:
    with _LOCK, _connect() as conn:
        rows = conn.execute(
            "SELECT project_id, created_at, stage, detail FROM events "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def event_count() -> int:
    with _LOCK, _connect() as conn:
        return int(conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"])


def reset() -> None:
    """Drop all stored rows. Used by the tests."""
    with _LOCK, _connect() as conn:
        conn.executescript(
            "DELETE FROM projects; DELETE FROM activity; DELETE FROM events;"
        )
