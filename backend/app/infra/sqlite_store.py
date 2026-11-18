"""Persistent, dependency-free event store for Easy Mode (single machine, no Docker).

Uses Python's built-in sqlite3. Suitable for lab-scale data (thousands to low
millions of events); OpenSearch remains the recommended store for larger setups.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.domain.memory_backends import aggregate_docs, filter_docs
from app.domain.query import EventQuery

_FMT = "%Y-%m-%dT%H:%M:%S.%f"


def _ts(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime(_FMT)


def _doc_ts(doc: dict) -> str:
    return _ts(datetime.fromisoformat(doc["@timestamp"].replace("Z", "+00:00")))


class SqliteEventStore:
    kind = "sqlite"

    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._db = sqlite3.connect(path, check_same_thread=False, timeout=30)
        self._db.execute("PRAGMA journal_mode=WAL")
        self.ensure_ready()

    def ensure_ready(self) -> None:
        with self._lock:
            self._db.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, ts TEXT NOT NULL, doc TEXT NOT NULL)")
            self._db.execute("CREATE INDEX IF NOT EXISTS ix_events_ts ON events(ts)")
            self._db.commit()

    def ping(self) -> bool:
        try:
            with self._lock:
                self._db.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def index(self, doc: dict) -> bool:
        with self._lock:
            cur = self._db.execute("INSERT OR IGNORE INTO events(id, ts, doc) VALUES (?,?,?)",
                                   (doc["event"]["id"], _doc_ts(doc), json.dumps(doc)))
            self._db.commit()
            return cur.rowcount == 1

    def exists(self, doc: dict) -> bool:
        with self._lock:
            return self._db.execute("SELECT 1 FROM events WHERE id=?", (doc["event"]["id"],)).fetchone() is not None

    def get(self, event_id: str) -> dict | None:
        with self._lock:
            row = self._db.execute("SELECT doc FROM events WHERE id=?", (event_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def _range(self, start: datetime, end: datetime) -> list[dict]:
        with self._lock:
            rows = self._db.execute("SELECT doc FROM events WHERE ts>=? AND ts<? ORDER BY ts DESC",
                                    (_ts(start), _ts(end))).fetchall()
        return [json.loads(r[0]) for r in rows]

    def search(self, q: EventQuery) -> tuple[int, list[dict]]:
        q.validate()
        return filter_docs(self._range(q.start, q.end), q)

    def aggregate(self, start: datetime, end: datetime, interval_minutes: int = 60) -> dict:
        return aggregate_docs(self._range(start, end), start, end, interval_minutes)

    def delete_older_than(self, days: int) -> int:
        cutoff = _ts(datetime.now(timezone.utc) - timedelta(days=days))
        with self._lock:
            cur = self._db.execute("DELETE FROM events WHERE ts<?", (cutoff,))
            self._db.commit()
            return cur.rowcount
