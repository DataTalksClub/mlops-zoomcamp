"""Simulation locale de l'agent Coûts (sans Docker, Redis ni Postgres).

Utilisée par la démo Streamlit. Toute la logique est ici, sans Streamlit,
pour pouvoir être testée.
"""
from __future__ import annotations

from datetime import datetime
from typing import Callable, List, Optional

from agents.cost import calculator
from agents.cost.agent import CostAgent
from agents.cost.collector import FakeCollector
from agents.cost.settings import CostConfig
from agents.cost.store import InMemoryCostStore
from common.events import Event


class RecordingBus:
    def __init__(self) -> None:
        self.events: List[dict] = []

    def publish(self, event: Event) -> None:
        self.events.append({"type": event.type.value, "payload": event.payload})


class RecordingLog:
    def __init__(self) -> None:
        self.rows: List[dict] = []

    def record(self, agent: str, action: str, model=None, details=None) -> None:
        self.rows.append({"agent": agent, "action": action, "details": details})


class Simulation:
    def __init__(self, config: Optional[CostConfig] = None,
                 clock: Callable[[], datetime] = datetime.now) -> None:
        self.config = config or CostConfig()
        self.clock = clock
        self.store = InMemoryCostStore()
        self.bus = RecordingBus()
        self.log = RecordingLog()
        self.collector = FakeCollector({"api": 0.0})
        self.agent = CostAgent(self.store, self.bus, self.log, self.config,
                               collector=self.collector, clock=clock)
        self.pending: Optional[dict] = None   # demande en attente de validation

    # ---- scénario 3, cases 1 à 3 : demande + estimation ----
    def request_retrain(self, model: str, months: int, requested_by: str) -> dict:
        answer = self.agent.handle_cost_estimate(
            {"model": model, "months": months, "requested_by": requested_by,
             "request_id": f"req-{len(self.bus.events) + 1}"}
        )
        self.pending = answer if answer["exceeds_budget"] else None
        if not answer["exceeds_budget"]:
            self._launch(answer, reason="sous le budget : lancement automatique")
        return answer

    # ---- case 4 : décision du responsable ----
    def approve(self) -> None:
        if self.pending is None:
            return
        answer, self.pending = self.pending, None
        self.log.record("humain", "approved", details={"request_id": answer["request_id"]})
        self._launch(answer, reason="approuvé par le responsable")

    def refuse(self) -> None:
        if self.pending is None:
            return
        answer, self.pending = self.pending, None
        self.log.record("humain", "refused", details={"request_id": answer["request_id"]})

    # ---- case 5 : exécution (simulée) ----
    def _launch(self, answer: dict, reason: str) -> None:
        self.log.record(
            "retrain",
            "retrain_started",
            model=answer["model"],
            details={"request_id": answer["request_id"], "reason": reason},
        )
        self.agent.handle_training_completed(
            {"model": answer["model"], "cpu_seconds": answer["estimated_cpu_seconds"],
             "months": answer["months"]}
        )

    # ---- autres actions de démo ----
    def add_training(self, model: str, cpu_seconds: float, months: int) -> float:
        return self.agent.handle_training_completed(
            {"model": model, "cpu_seconds": cpu_seconds, "months": months})

    def advance_api_cpu(self, model: str, cpu_seconds: float) -> float:
        """Fait avancer le compteur CPU du conteneur 'api' et facture le delta."""
        self.agent.record_serving_sample(model, "api")  # amorce si 1er appel
        self.collector.values["api"] += cpu_seconds
        return self.agent.record_serving_sample(model, "api")

    # ---- lectures ----
    def month(self) -> str:
        return calculator.month_key(self.clock())

    def month_total(self) -> float:
        return self.store.month_total(self.month())

    def budget_ratio(self) -> float:
        if self.config.monthly_budget <= 0:
            return 1.0
        return min(1.0, self.month_total() / self.config.monthly_budget)
