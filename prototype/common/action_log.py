"""Journal d'actions : chaque décision ou action d'un agent y est écrite.
Grafana lit la table action_log dans Postgres."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Integer, MetaData, String, Table, create_engine, insert, select

from common import config

metadata = MetaData()

action_log = Table(
    "action_log",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", DateTime(timezone=True), nullable=False),
    Column("agent", String(64), nullable=False),
    Column("action", String(128), nullable=False),
    Column("model", String(128)),
    Column("details", JSON),
)


class ActionLog:
    def __init__(self, url: str = config.DATABASE_URL):
        self.engine = create_engine(url)
        metadata.create_all(self.engine)

    def record(self, agent: str, action: str, model: str | None = None, details: dict[str, Any] | None = None) -> None:
        with self.engine.begin() as conn:
            conn.execute(insert(action_log).values(
                timestamp=datetime.now(timezone.utc), agent=agent, action=action,
                model=model, details=details or {},
            ))

    def latest(self, limit: int = 20) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(action_log).order_by(action_log.c.id.desc()).limit(limit))
            return [dict(r._mapping) for r in rows]