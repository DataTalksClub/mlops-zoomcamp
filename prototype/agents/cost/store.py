"""Stockage des coûts : interface + implémentation en mémoire + Postgres."""
from __future__ import annotations

from typing import Dict, List, Protocol, Tuple

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS model_costs (
    id          SERIAL PRIMARY KEY,
    ts          TIMESTAMPTZ NOT NULL DEFAULT now(),
    model       TEXT NOT NULL,
    month       TEXT NOT NULL,
    kind        TEXT NOT NULL,            -- 'training' ou 'serving'
    cpu_seconds DOUBLE PRECISION NOT NULL,
    months      INTEGER,                  -- mois de données (entraînement)
    cost        DOUBLE PRECISION NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_model_costs_month ON model_costs (month, model);
"""


class CostStore(Protocol):
    def add(self, model: str, month: str, kind: str, cpu_seconds: float,
            cost: float, months: int | None = None) -> None: ...

    def month_total(self, month: str) -> float: ...

    def by_model(self, month: str) -> Dict[str, float]: ...

    def training_history(self, model: str) -> List[Tuple[float, int]]: ...


class InMemoryCostStore:
    """Pour les tests et le développement sans base de données."""

    def __init__(self) -> None:
        self._rows: List[dict] = []

    def add(self, model, month, kind, cpu_seconds, cost, months=None):
        self._rows.append(dict(model=model, month=month, kind=kind,
                               cpu_seconds=cpu_seconds, cost=cost, months=months))

    def month_total(self, month):
        return sum(r["cost"] for r in self._rows if r["month"] == month)

    def by_model(self, month):
        out: Dict[str, float] = {}
        for r in self._rows:
            if r["month"] == month:
                out[r["model"]] = out.get(r["model"], 0.0) + r["cost"]
        return out

    def training_history(self, model):
        return [(r["cpu_seconds"], r["months"]) for r in self._rows
                if r["model"] == model and r["kind"] == "training" and r["months"]]


class PostgresCostStore:
    """Implémentation Postgres. `conn` est une connexion psycopg2."""

    def __init__(self, conn) -> None:
        self._conn = conn
        with self._conn.transaction(), self._conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)

    def add(self, model, month, kind, cpu_seconds, cost, months=None):
        with self._conn.transaction(), self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO model_costs (model, month, kind, cpu_seconds, months, cost) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (model, month, kind, cpu_seconds, months, cost),
            )

    def month_total(self, month):
        with self._conn.transaction(), self._conn.cursor() as cur:
            cur.execute("SELECT COALESCE(SUM(cost), 0) FROM model_costs WHERE month = %s",
                        (month,))
            return float(cur.fetchone()[0])

    def by_model(self, month):
        with self._conn.transaction(), self._conn.cursor() as cur:
            cur.execute("SELECT model, SUM(cost) FROM model_costs "
                        "WHERE month = %s GROUP BY model", (month,))
            return {m: float(c) for m, c in cur.fetchall()}

    def training_history(self, model):
        with self._conn.transaction(), self._conn.cursor() as cur:
            cur.execute("SELECT cpu_seconds, months FROM model_costs "
                        "WHERE model = %s AND kind = 'training' AND months > 0", (model,))
            return [(float(c), int(m)) for c, m in cur.fetchall()]
