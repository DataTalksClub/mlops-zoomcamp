"""Agent Coûts.

Événements écoutés :
  - cost_estimate      {model, months?, requested_by?, request_id?}
  - training_completed {model, cpu_seconds, months?}

Événements publiés :
  - cost_estimated       réponse à cost_estimate (options standard / spot)
  - budget_exceeded      si coût du mois + estimation > budget
  - cost_recommendation  taille de serveur, scale-to-zero (calcul seulement)

L'agent ne bloque JAMAIS un job : c'est l'Orchestrateur qui décide
(validation humaine). Aucun appel à un LLM ici.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, Optional, Protocol

from . import calculator, pricing, recommender
from .collector import CpuCollector
from .settings import CostConfig
from .store import CostStore
from common.events import Event, EventType


class EventBus(Protocol):
    def publish(self, event: Event) -> None: ...


class ActionLog(Protocol):
    def record(
        self, agent: str, action: str, model: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None: ...


AGENT_NAME = "cost"


class CostAgent:
    def __init__(
        self,
        store: CostStore,
        bus: EventBus,
        action_log: ActionLog,
        config: Optional[CostConfig] = None,
        collector: Optional[CpuCollector] = None,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self.store = store
        self.bus = bus
        self.action_log = action_log
        self.config = config or CostConfig()
        self.collector = collector
        self.clock = clock
        self._last_cpu: Dict[str, float] = {}

    def on_event(self, event: Event) -> None:
        payload = {**event.payload, "model": event.model}
        if event.type == EventType.COST_ESTIMATE:
            self.handle_cost_estimate(payload)
        elif event.type == EventType.TRAINING_COMPLETED:
            self.handle_training_completed(payload)

    # ---- estimation avant un retrain ----
    def handle_cost_estimate(self, payload: dict) -> dict:
        model = payload["model"]
        months = payload.get("months")
        month = calculator.month_key(self.clock())

        cpu = calculator.estimate_cpu_seconds(
            self.store.training_history(model),
            months,
            self.config.default_cpu_seconds_per_month_of_data,
        )
        options = pricing.price_options(cpu, self.config)
        estimate = options["standard"]["cost"]
        month_total = self.store.month_total(month)
        budget = self.config.monthly_budget
        exceeds = calculator.would_exceed(month_total, estimate, budget)

        answer = {
            "request_id": payload.get("request_id"),
            "requested_by": payload.get("requested_by"),
            "model": model,
            "months": months,
            "estimated_cpu_seconds": round(cpu, 3),
            "options": options,
            "month_total": round(month_total, 6),
            "budget": budget,
            "exceeds_budget": exceeds,
        }
        self._publish(EventType.COST_ESTIMATED, model, answer)
        self._record("cost_estimated", model, answer)

        if exceeds:
            over = {**answer, "over_by": round(month_total + estimate - budget, 6)}
            self._publish(EventType.BUDGET_EXCEEDED, model, over)
            self._record("budget_exceeded", model, over)
        return answer

    # ---- enregistrement d'un entraînement terminé ----
    def handle_training_completed(self, payload: dict) -> float:
        model = payload["model"]
        cpu = float(payload["cpu_seconds"])
        value = calculator.cost(cpu, self.config.cost_per_cpu_second)
        month = calculator.month_key(self.clock())
        self.store.add(model, month, "training", cpu, value, payload.get("months"))
        self._record(
            "cost_recorded", model,
            {"kind": "training", "cpu_seconds": cpu, "cost": value},
        )
        return value

    # ---- coût de l'API servie (à appeler périodiquement) ----
    def record_serving_sample(self, model: str, container: str) -> float:
        """Enregistre le CPU consommé par `container` depuis le dernier appel."""
        if self.collector is None:
            raise RuntimeError("aucun collecteur CPU configuré")
        current = self.collector.cpu_seconds(container)
        previous = self._last_cpu.get(container)
        self._last_cpu[container] = current
        if previous is None or current < previous:  # 1er appel ou conteneur redémarré
            return 0.0
        delta = current - previous
        value = calculator.cost(delta, self.config.cost_per_cpu_second)
        month = calculator.month_key(self.clock())
        self.store.add(model, month, "serving", delta, value)
        self._record(
            "cost_recorded", model,
            {"kind": "serving", "container": container, "cpu_seconds": delta, "cost": value},
        )
        return value

    # ---- recommandations (aucune action sur l'infrastructure) ----
    def recommend_server_size(self, model: str, used_vcpus: float, current_size: str) -> dict:
        rec = recommender.recommend_size(used_vcpus, current_size, self.config)
        rec = {**rec, "model": model}
        self._publish_recommendation(rec)
        return rec

    def check_idle(self, model: str, last_request_at: Optional[datetime],
                   size: str, idle_hours: float) -> Optional[dict]:
        if not recommender.is_idle(last_request_at, self.clock(), self.config):
            return None
        rec = recommender.scale_to_zero_saving(idle_hours, size, self.config)
        rec = {**rec, "model": model}
        self._publish_recommendation(rec)
        return rec

    def _publish_recommendation(self, rec: dict) -> None:
        self._publish(EventType.COST_RECOMMENDATION, rec["model"], rec)
        self._record("cost_recommendation", rec["model"], rec)

    def _publish(self, event_type: EventType, model: str, payload: dict[str, Any]) -> None:
        self.bus.publish(Event(
            type=event_type,
            source="agent_cost",
            model=model,
            payload=payload,
        ))

    def _record(self, action: str, model: str, details: dict[str, Any]) -> None:
        self.action_log.record(AGENT_NAME, action, model=model, details=details)
