"""Orchestrateur : le chef d'orchestre des 4 agents.

Il n'entraîne, ne répare et ne calcule rien lui-même. Pour chaque événement
reçu, il décide de la suite selon rules/autonomy.yaml et prévient l'humain
sur la page web (notifier).

Écoute : drift_detected, cost_estimated, approval_given, model_registered,
         model_promoted, promotion_blocked, action_logged, incident_opened,
         incident_resolved, approval_requested
Publie : cost_estimate, retrain_requested, approval_requested,
         training_completed, incident_opened (données corrompues)
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Callable

from agents.orchestrator.rules import APPROVAL, AUTO, Rules
from common import config
from common.events import Event, EventType, Severity

AGENT = "orchestrator"
RETRAIN = "agent_retrain"  # nom de source de l'agent Retrain

LISTENED = [
    EventType.DRIFT_DETECTED, EventType.COST_ESTIMATED, EventType.APPROVAL_GIVEN,
    EventType.MODEL_REGISTERED, EventType.MODEL_PROMOTED, EventType.PROMOTION_BLOCKED,
    EventType.ACTION_LOGGED, EventType.INCIDENT_OPENED, EventType.INCIDENT_RESOLVED,
    EventType.APPROVAL_REQUESTED,
]


class Orchestrator:
    def __init__(self, bus, log, notifier, rules: Rules | None = None,
                 clock: Callable[[], float] = time.time):
        self.bus = bus
        self.log = log
        self.notifier = notifier
        self.rules = rules or Rules()
        self.clock = clock
        self.pending: dict[str, dict] = {}  # request_id -> demande en cours (étape "cost" ou "approval")
        self.retrain_since: float | None = None  # heure de la dernière demande de retrain

    def run(self) -> None:
        print("Orchestrateur : en écoute…")
        self.bus.listen(self.handle, types=LISTENED)

    def handle(self, event: Event) -> None:
        if event.source == AGENT:
            return  # nos propres événements reviennent par Redis : on les ignore
        handlers = {
            EventType.DRIFT_DETECTED: self.on_drift,
            EventType.COST_ESTIMATED: self.on_cost_estimated,
            EventType.APPROVAL_GIVEN: self.on_approval,
            EventType.MODEL_REGISTERED: self.on_model_registered,
            EventType.MODEL_PROMOTED: self.on_model_promoted,
            EventType.PROMOTION_BLOCKED: self.on_promotion_blocked,
            EventType.ACTION_LOGGED: self.on_action_logged,
            EventType.INCIDENT_OPENED: self.on_incident_opened,
            EventType.INCIDENT_RESOLVED: self.on_incident_resolved,
            EventType.APPROVAL_REQUESTED: self.on_approval_requested,
        }
        handler = handlers.get(event.type)
        if handler:
            handler(event)

    # ------------------------------------------------ dérive -> coût -> retrain
    def on_drift(self, event: Event) -> None:
        p = event.payload
        if p.get("reason") == "corrupted_input_data":
            # On n'entraîne jamais sur des données cassées
            details = {"cause": "corrupted_input_data", "invalid_share": p.get("invalid_share"),
                       "invalid_reasons": p.get("invalid_reasons")}
            self.publish(EventType.INCIDENT_OPENED, Severity.CRITICAL, details)
            self.record("retrain_refused_corrupted_data", details)
            self.notifier.notify(
                f"🚨 Données corrompues ({p.get('invalid_share', 0):.0%} de lignes invalides) : "
                "pas de réentraînement. Il faut vérifier la source des données.")
            return

        if self.busy():
            self.record("drift_ignored", {"reason": "une demande est déjà en cours"})
            return

        request_id = uuid.uuid4().hex[:8]
        self.pending[request_id] = {"step": "cost", "drift": p}
        self.publish(EventType.COST_ESTIMATE, Severity.INFO, {
            "request_id": request_id, "requested_by": AGENT, "months": config.DEFAULT_TRAIN_MONTHS})
        self.record("cost_requested", {"request_id": request_id, "drift_score": p.get("drift_score")})

    def on_cost_estimated(self, event: Event) -> None:
        p = event.payload
        request_id = p.get("request_id")
        request = self.pending.get(request_id)
        if not request or request["step"] != "cost":
            return  # une estimation demandée par quelqu'un d'autre

        cost = p["options"]["standard"]["cost"]
        action = "retrain_over_budget" if p.get("exceeds_budget") else "retrain"
        rule = self.rules.can(action)
        details = {"request_id": request_id, "action": action, "rule": rule, "estimated_cost": cost,
                   "month_total": p.get("month_total"), "budget": p.get("budget")}
        self.record("retrain_decision", details)

        if rule == AUTO:
            del self.pending[request_id]
            self.request_retrain(request_id, approved_by=None)
        elif rule == APPROVAL:
            request["step"] = "approval"
            self.publish(EventType.APPROVAL_REQUESTED, Severity.WARNING, details)
            self.notifier.ask(
                f"Dérive détectée. Réentraîner coûte {cost:.2f} € ; ce mois : {p.get('month_total', 0):.2f} € "
                f"sur un budget de {p.get('budget', 0):.2f} €. On réentraîne ?", request_id)
        else:  # forbidden
            del self.pending[request_id]
            self.notifier.notify(f"⛔ Réentraînement interdit par les règles ({action}).")

    def on_approval(self, event: Event) -> None:
        p = event.payload
        request_id = p.get("request_id")
        request = self.pending.get(request_id)
        if not request or request["step"] != "approval":
            return
        del self.pending[request_id]
        who = p.get("approved_by", "?")
        if p.get("approved"):
            self.request_retrain(request_id, approved_by=who)
        else:
            self.record("retrain_refused", {"request_id": request_id, "refused_by": who})
            self.notifier.notify(f"Réentraînement refusé par {who}. La production ne change pas.")

    def request_retrain(self, request_id: str, approved_by: str | None) -> None:
        self.retrain_since = self.clock()
        payload = {"request_id": request_id, "requested_by": AGENT, "approved_by": approved_by}
        self.publish(EventType.RETRAIN_REQUESTED, Severity.INFO, payload)
        self.record("retrain_requested", payload)
        by = f", validé par {approved_by}" if approved_by else ""
        self.notifier.notify(f"🔄 Dérive détectée : réentraînement lancé{by}.")

    def busy(self) -> bool:
        """Une demande attend déjà (coût ou humain), ou un retrain tourne encore."""
        if self.pending:
            return True
        if self.retrain_since is None:
            return False
        return self.clock() - self.retrain_since < config.RETRAIN_TIMEOUT_MINUTES * 60

    # ------------------------------------------------ résultats de Retrain
    def on_model_registered(self, event: Event) -> None:
        # Traduction pour l'agent Coûts, qui attend training_completed
        p = event.payload
        self.publish(EventType.TRAINING_COMPLETED, Severity.INFO, {
            "cpu_seconds": p.get("training_seconds", 0.0), "months": len(p.get("period") or []) or None,
            "version": p.get("version")})

    def on_model_promoted(self, event: Event) -> None:
        self.retrain_since = None
        p = event.payload
        if p.get("production_rmse") is None:
            text = f"✅ Premier modèle v{p['challenger_version']} mis en production (RMSE {p['challenger_rmse']:.2f})."
        else:
            text = (f"✅ Modèle v{p['challenger_version']} promu : RMSE {p['challenger_rmse']:.2f} contre "
                    f"{p['production_rmse']:.2f} pour v{p['production_version']} ({p['improvement']:.1%} d'erreur en moins).")
        self.notifier.notify(text)

    def on_promotion_blocked(self, event: Event) -> None:
        self.retrain_since = None
        p = event.payload
        self.notifier.notify(
            f"⛔ Promotion bloquée : v{p['challenger_version']} a un RMSE de {p['challenger_rmse']:.2f} contre "
            f"{p['production_rmse']:.2f} pour la production v{p['production_version']} "
            f"(gain {p['improvement']:.1%}, minimum {p['min_improvement']:.0%}). La production ne change pas.")

    def on_action_logged(self, event: Event) -> None:
        p = event.payload
        if p.get("action") == "retrain_skipped":
            self.retrain_since = None
            self.notifier.notify(f"Réentraînement ignoré par Retrain : {p.get('reason')}.")

    # ------------------------------------------------ incidents (Fiabilité, Retrain)
    def on_incident_opened(self, event: Event) -> None:
        p = event.payload
        if event.source == RETRAIN:
            self.retrain_since = None
            self.notifier.notify(f"🚨 L'entraînement a échoué : {p.get('error')}. La production ne change pas.")
            return
        self.notifier.notify(
            f"🚨 Incident {p.get('incident_id')} : {p.get('cause')} sur {p.get('component')} "
            f"(niveau {p.get('level')}). L'agent Fiabilité s'en occupe.")

    def on_incident_resolved(self, event: Event) -> None:
        p = event.payload
        actions = ", ".join(a["action"] for a in p.get("actions", [])) or "aucune"
        self.notifier.notify(
            f"✅ Incident {p.get('incident_id')} résolu en {p.get('duration_seconds', 0):.0f} s "
            f"(actions : {actions}).")

    def on_approval_requested(self, event: Event) -> None:
        p = event.payload
        self.notifier.notify(
            f"🙋 L'agent {event.source} demande une intervention humaine : {p.get('reason')} "
            f"(incident {p.get('incident_id')}).")

    # ------------------------------------------------ outils
    def publish(self, type_: EventType, severity: Severity, payload: dict[str, Any]) -> None:
        self.bus.publish(Event(type=type_, source=AGENT, severity=severity, payload=payload))

    def record(self, action: str, details: dict[str, Any]) -> None:
        self.log.record(AGENT, action, config.MODEL_NAME, details)