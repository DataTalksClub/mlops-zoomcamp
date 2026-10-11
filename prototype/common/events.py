"""Contrat d'événements commun aux 5 agents.
Les agents ne s'appellent jamais directement : ils publient et écoutent des
événements JSON sur un canal Redis. Toute modification se valide en équipe."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Iterable

import redis
from pydantic import BaseModel, Field

from common import config


class EventType(str, Enum):
    DRIFT_DETECTED = "drift_detected"
    QUALITY_OK = "quality_ok"
    RETRAIN_REQUESTED = "retrain_requested"
    MODEL_REGISTERED = "model_registered"
    MODEL_PROMOTED = "model_promoted"
    PROMOTION_BLOCKED = "promotion_blocked"
    INCIDENT_OPENED = "incident_opened"
    INCIDENT_RESOLVED = "incident_resolved"
    COST_ESTIMATE = "cost_estimate"
    BUDGET_EXCEEDED = "budget_exceeded"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GIVEN = "approval_given"
    ACTION_LOGGED = "action_logged"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Event(BaseModel):
    type: EventType
    source: str  # ex. "agent_qualite"
    model: str = config.MODEL_NAME
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: Severity = Severity.INFO
    payload: dict[str, Any] = Field(default_factory=dict)

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, raw: str | bytes) -> "Event":
        return cls.model_validate_json(raw)


class EventBus:
    """Publication et écoute des événements sur Redis pub/sub."""

    def __init__(self, client: redis.Redis | None = None, channel: str = config.EVENTS_CHANNEL):
        self.client = client or redis.Redis.from_url(config.REDIS_URL)
        self.channel = channel

    def publish(self, event: Event) -> None:
        self.client.publish(self.channel, event.to_json())

    def listen(self, handler: Callable[[Event], None], types: Iterable[EventType] | None = None) -> None:
        """Appelle handler pour chaque événement reçu (bloquant).
        types limite l'écoute aux événements qui concernent l'agent."""
        wanted = set(types) if types else None
        pubsub = self.client.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(self.channel)
        for message in pubsub.listen():
            event = Event.from_json(message["data"])
            if wanted is None or event.type in wanted:
                handler(event)