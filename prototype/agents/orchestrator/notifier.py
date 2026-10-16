"""Messages pour l'humain, affichés sur la page web de l'orchestrateur.

Ils sont rangés dans la table notifications de Postgres :
- kind="info"     : simple message (modèle promu, incident...) ;
- kind="question" : demande de validation, status pending -> approved / refused."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (Column, DateTime, Integer, MetaData, String, Table, Text,
                        create_engine, insert, select, update)

from common import config

metadata = MetaData()

notifications = Table(
    "notifications",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", DateTime(timezone=True), nullable=False),
    Column("kind", String(16), nullable=False),
    Column("text", Text, nullable=False),
    Column("request_id", String(64)),
    Column("status", String(16)),
    Column("answered_by", String(64)),
)


class Notifier:
    def __init__(self, url: str = config.DATABASE_URL):
        self.engine = create_engine(url)
        metadata.create_all(self.engine)

    def _insert(self, **values) -> None:
        with self.engine.begin() as conn:
            conn.execute(insert(notifications).values(timestamp=datetime.now(timezone.utc), **values))

    def notify(self, text: str) -> None:
        print(f"[notification] {text}")
        self._insert(kind="info", text=text)

    def ask(self, text: str, request_id: str) -> None:
        """Question avec les boutons Valider / Refuser sur la page web."""
        print(f"[question {request_id}] {text}")
        self._insert(kind="question", text=text, request_id=request_id, status="pending")

    def answer(self, request_id: str, approved: bool, who: str) -> bool:
        """Enregistre la réponse. False si la question n'existe pas ou a déjà une réponse."""
        with self.engine.begin() as conn:
            result = conn.execute(
                update(notifications)
                .where(notifications.c.request_id == request_id, notifications.c.status == "pending")
                .values(status="approved" if approved else "refused", answered_by=who))
        return result.rowcount == 1

    def latest(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(notifications).order_by(notifications.c.id.desc()).limit(limit))
            return [dict(r._mapping) for r in rows]