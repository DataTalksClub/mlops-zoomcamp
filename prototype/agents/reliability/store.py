"""Historique des mesures de l'agent Fiabilité (une ligne par cycle), lu par Grafana.

Le journal d'actions dit ce que l'agent a fait ; cette table dit ce qu'il a vu :
taux d'erreurs, latence, budget SLO, état du service, à chaque cycle."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (Boolean, Column, DateTime, Float, Integer, MetaData, String, Table,
                        create_engine, insert, select)

from common import config

metadata = MetaData()

reliability_metrics = Table(
    "reliability_metrics",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", DateTime(timezone=True), nullable=False, index=True),
    Column("reachable", Boolean, nullable=False),
    Column("requests", Float, nullable=False),
    Column("error_rate", Float, nullable=False),
    Column("p95_latency", Float),
    Column("probe_failure_rate", Float, nullable=False),
    Column("budget_consumed", Float, nullable=False),
    Column("degraded", Boolean, nullable=False),
    Column("incident_level", String(16)),          # NULL = pas d'incident
)


class MetricsStore:
    def __init__(self, url: str = config.DATABASE_URL):
        self.engine = create_engine(url)
        metadata.create_all(self.engine)

    def record(self, now: float, **values) -> None:
        with self.engine.begin() as conn:
            conn.execute(insert(reliability_metrics).values(
                timestamp=datetime.fromtimestamp(now, tz=timezone.utc), **values))

    def latest(self, limit: int = 20) -> list[dict]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(reliability_metrics)
                                .order_by(reliability_metrics.c.id.desc()).limit(limit))
            return [dict(r._mapping) for r in rows]
