"""Agent Fiabilité : surveiller -> détecter -> diagnostiquer -> agir -> vérifier -> clore.

Un cycle (run_once) toutes les RELIABILITY_POLL_SECONDS :
  1. sondes sur le vrai modèle, puis lecture de /metrics ;
  2. sans incident : 2 dépassements de suite ouvrent un incident ;
  3. avec incident : 2 cycles OK de suite le clôturent ; sinon on recalcule la
     gravité (elle ne fait que monter) et on passe à l'action suivante.

Les actions viennent du playbook du diagnostic. Un "remediator" (le LLM validé
par le juge) pourra choisir l'action à la place du playbook en niveau moyen ou
élevé ; il sera branché plus tard. Toute décision est publiée sur le bus et
écrite dans le journal d'actions. L'agent ne s'arrête jamais sur une erreur."""
from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import yaml

from agents.reliability.actions import ActionResult, ReliabilityActions
from agents.reliability.catalog import Action
from agents.reliability.diagnosis import Diagnosis, Signals, diagnose
from agents.reliability.metrics import Snapshot, WindowStats, compute_window, fetch_snapshot
from agents.reliability.probes import ProbeResult, run_probes
from agents.reliability.severity import (
    ErrorBudget, IncidentContext, SeverityResult, compute_severity, escalate, is_breach,
)
from agents.reliability.signals import SignalCollector
from common import config
from common.events import Event, EventType, Severity

AGENT_NAME = "agent_fiabilite"
AUTONOMY_FILE = Path(__file__).resolve().parents[2] / "rules" / "autonomy.yaml"
AUTONOMY_KEYS = {
    Action.RESTART_API: "restart_api",
    Action.RECREATE_API: "recreate_api",
    Action.RELOAD_MODEL: "reload_model",
    Action.ROLLBACK_MODEL: "rollback_model",
    Action.DEGRADED_MODE: "degraded_mode",
    Action.RESTART_REDIS: "restart_redis",
    Action.RESTART_MLFLOW: "restart_mlflow",
}
RESTART_ACTIONS = {Action.RESTART_API, Action.RECREATE_API}

log = logging.getLogger(AGENT_NAME)

# remediator(incident, window, signals) -> Action ou None (None = suivre le playbook)
Remediator = Callable[["Incident", WindowStats, Signals], "Action | None"]


def load_autonomy(path: Path = AUTONOMY_FILE) -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@dataclass
class Incident:
    id: str
    opened_at: float
    diagnosis: Diagnosis
    level: Severity
    severity: SeverityResult
    next_step: int = 0                              # position dans le playbook
    failed_repairs: int = 0
    pending: tuple[Action, float] | None = None     # action en attente de vérification
    degraded: bool = False
    reapply_degraded: bool = False                  # un redémarrage a effacé le mode dégradé de l'API
    human_notified_at: float | None = None
    exhausted: bool = False                         # plus aucune action automatique à tenter
    tried: set = field(default_factory=set)         # actions déjà tentées (jamais deux fois par incident)
    actions: list[dict] = field(default_factory=list)
    timeline: list[dict] = field(default_factory=list)

    def note(self, now: float, event: str, **details) -> None:
        self.timeline.append({"t": round(now - self.opened_at, 1), "event": event, **details})


class ReliabilityAgent:
    def __init__(self, bus=None, action_log=None, actions=None, collector=None,
                 fetch: Callable[[], Snapshot] = fetch_snapshot,
                 probe: Callable[[], ProbeResult] = run_probes,
                 autonomy: dict[str, str] | None = None,
                 remediator: Remediator | None = None,
                 metrics_store=None):
        if bus is None:
            from common.events import EventBus
            bus = EventBus()
        if action_log is None:
            from common.action_log import ActionLog
            action_log = ActionLog()
        if metrics_store is None:
            from agents.reliability.store import MetricsStore
            metrics_store = MetricsStore()
        self.bus = bus
        self.action_log = action_log
        self.metrics_store = metrics_store
        self.actions = actions or ReliabilityActions()
        self.collector = collector or SignalCollector()
        self.fetch = fetch
        self.probe = probe
        self.autonomy = load_autonomy() if autonomy is None else autonomy
        self.remediator = remediator
        self.budget = ErrorBudget()
        self.prev: Snapshot | None = None
        self.breaches = 0
        self.ok_streak = 0
        self.incident: Incident | None = None
        self.closed_at: deque[float] = deque()     # clôtures récentes (critère "historique")
        self.restarts: deque[float] = deque()      # redémarrages récents (anti-boucle)

    # ------------------------------------------------------------------ boucle
    def run_forever(self) -> None:
        log.info("Agent Fiabilité démarré (cycle de %.0f s)", config.RELIABILITY_POLL_SECONDS)
        while True:
            started = time.time()
            try:
                self.run_once(started)
            except Exception as exc:  # l'agent ne doit jamais être plus fragile que ce qu'il surveille
                log.exception("Erreur inattendue dans le cycle")
                self._record("agent_error", {"error": repr(exc)})
            time.sleep(max(0.0, config.RELIABILITY_POLL_SECONDS - (time.time() - started)))

    def run_once(self, now: float | None = None) -> WindowStats | None:
        now = time.time() if now is None else now
        probes = self.probe()          # avant /metrics : les sondes comptent dans la fenêtre
        snap = self.fetch()
        if self.prev is None:          # premier cycle : pas encore de fenêtre à comparer
            self.prev = snap
            return None
        window = compute_window(self.prev, snap)
        if snap.reachable:  # la base de comparaison reste la dernière lecture réussie
            self.prev = snap
        self.budget.add(window, now)
        self.collector.observe(window, now)   # suivi continu (ex. changement de version du modèle)
        unhealthy = is_breach(window) or not probes.ok

        if self.incident is None:
            self._watch(window, probes, unhealthy, now)
        else:
            self._handle(window, probes, unhealthy, now)
        self._store_metrics(window, probes, now)
        return window

    def _store_metrics(self, window: WindowStats, probes: ProbeResult, now: float) -> None:
        """Une ligne par cycle pour les courbes Grafana (ce que l'agent a vu)."""
        inc = self.incident
        try:
            self.metrics_store.record(
                now,
                reachable=window.reachable,
                requests=window.requests,
                error_rate=window.error_rate,
                p95_latency=window.p95_latency,
                probe_failure_rate=probes.failure_rate,
                budget_consumed=self.budget.consumed(),
                degraded=bool(inc and inc.degraded),
                incident_level=inc.level.value if inc else None,
            )
        except Exception as exc:  # Postgres en panne : l'agent continue
            log.error("Écriture des mesures impossible : %s", exc)

    # --------------------------------------------------------- sans incident
    def _watch(self, window: WindowStats, probes: ProbeResult, unhealthy: bool, now: float) -> None:
        if not unhealthy:
            self.breaches = 0
            return
        self.breaches += 1
        log.info("Dépassement de seuil %d/%d", self.breaches, config.CONSECUTIVE_BREACHES)
        if self.breaches >= config.CONSECUTIVE_BREACHES:
            self._open(window, probes, now)

    def _open(self, window: WindowStats, probes: ProbeResult, now: float) -> None:
        signals = self.collector.collect(window, now)
        diag = diagnose(window, signals)
        sev = compute_severity(window, self.budget.consumed(), self._context(diag, None, now))
        inc = Incident(id=f"inc-{int(now)}", opened_at=now, diagnosis=diag, level=sev.level, severity=sev)
        inc.note(now, "opened", cause=diag.cause.value, level=sev.level.value, score=sev.score)
        self.incident, self.breaches, self.ok_streak = inc, 0, 0
        log.warning("Incident %s ouvert : %s (%s, score %d)", inc.id, diag.cause.value, sev.level.value, sev.score)
        self._publish(EventType.INCIDENT_OPENED, sev.level, {
            **self._summary(inc, window, probes), "breakdown": sev.breakdown, "forced_reason": sev.forced_reason,
        })
        self._record("incident_opened", self._summary(inc, window, probes))
        self._act(window, signals, now)

    # --------------------------------------------------------- avec incident
    def _handle(self, window: WindowStats, probes: ProbeResult, unhealthy: bool, now: float) -> None:
        inc = self.incident
        if not unhealthy:
            self.ok_streak += 1
            inc.note(now, "check_ok", streak=self.ok_streak)
            if self.ok_streak >= config.CONSECUTIVE_OK_TO_RESOLVE:
                self._resolve(now)
            return
        self.ok_streak = 0

        signals = self.collector.collect(window, now)
        diag = diagnose(window, signals)
        # Pendant la vérification d'une action, le système est en transition (ex. API qui
        # redémarre) : un nouveau diagnostic serait trompeur, on garde l'actuel.
        if diag.cause != inc.diagnosis.cause and inc.pending is None:
            inc.note(now, "diagnosis_changed", old=inc.diagnosis.cause.value, new=diag.cause.value)
            inc.diagnosis, inc.next_step = diag, 0
        else:
            diag = inc.diagnosis

        # Gravité figée elle aussi pendant la vérification d'une action : une API qui redémarre
        # est injoignable quelques secondes, ce qui ne doit pas déclencher le niveau critique.
        if inc.pending is None:
            sev = compute_severity(window, self.budget.consumed(), self._context(diag, inc, now))
            level = escalate(inc.level, sev.level)
            if level != inc.level:
                inc.note(now, "level_up", old=inc.level.value, new=level.value, score=sev.score)
                log.warning("Incident %s : niveau %s -> %s", inc.id, inc.level.value, level.value)
            inc.level, inc.severity = level, sev
        self._act(window, signals, now)

    def _act(self, window: WindowStats, signals: Signals, now: float) -> None:
        inc = self.incident

        # Niveau élevé : l'humain est prévenu tout de suite et le service passe en mode dégradé
        # (sauf pendant la vérification d'une action : le système est en transition).
        if inc.level == Severity.CRITICAL and inc.human_notified_at is None:
            self._notify_human(now, "niveau critique")
        if (inc.level == Severity.CRITICAL and Action.DEGRADED_MODE not in inc.tried
                and window.reachable and inc.pending is None):
            self._execute(Action.DEGRADED_MODE, now)

        # Un redémarrage a effacé le mode dégradé (état en mémoire de l'API) : on le remet.
        if inc.reapply_degraded and window.reachable:
            inc.reapply_degraded = False
            self._execute(Action.DEGRADED_MODE, now)

        # Action en cours : on lui laisse le temps d'agir avant de la juger.
        if inc.pending:
            action, started = inc.pending
            elapsed = now - started
            # Délai minimal, prolongé tant que l'API n'a pas fini de redémarrer (/health KO),
            # dans la limite de VERIFY_MAX_WAIT_SECONDS.
            if elapsed < config.VERIFY_WAIT_SECONDS or (
                    not window.health_ok and elapsed < config.VERIFY_MAX_WAIT_SECONDS):
                return
            inc.pending = None
            inc.failed_repairs += 1
            inc.note(now, "action_ineffective", action=action.value)

        if inc.exhausted:  # plus rien à tenter : on rappelle l'humain régulièrement
            if now - (inc.human_notified_at or 0) >= config.ESCALATION_REMINDER_MINUTES * 60:
                self._notify_human(now, "rappel : incident toujours ouvert")
            return

        action = self._next_action(window, signals)
        if action is None or action == Action.ESCALATE:
            inc.exhausted = True
            inc.note(now, "playbook_exhausted")
            self._notify_human(now, "toutes les actions automatiques ont été tentées")
            return
        self._execute(action, now, verify=action != Action.DEGRADED_MODE)

    def _next_action(self, window: WindowStats, signals: Signals) -> Action | None:
        inc = self.incident
        if self.remediator and inc.level in (Severity.WARNING, Severity.CRITICAL):
            choice = self.remediator(inc, window, signals)
            if choice is not None:
                return choice
        playbook = inc.diagnosis.playbook
        while inc.next_step < len(playbook):
            action = playbook[inc.next_step]
            inc.next_step += 1
            if action in inc.tried:
                continue  # une action déjà tentée dans cet incident n'est pas répétée
            return action
        return None

    def _execute(self, action: Action, now: float, verify: bool = False) -> ActionResult | None:
        inc = self.incident
        rule = self.autonomy.get(AUTONOMY_KEYS.get(action, ""), "approval")
        if rule != "auto":
            inc.note(now, "action_not_allowed", action=action.value, rule=rule)
            if rule == "approval":
                self._publish(EventType.APPROVAL_REQUESTED, inc.level, {
                    "incident_id": inc.id, "action": action.value, "reason": "validation humaine requise"})
            return None
        if action in RESTART_ACTIONS:
            while self.restarts and now - self.restarts[0] > 3600:
                self.restarts.popleft()
            if len(self.restarts) >= config.MAX_RESTARTS_PER_HOUR:
                inc.note(now, "action_skipped", action=action.value, reason="trop de redémarrages dans l'heure")
                return None
            self.restarts.append(now)

        inc.tried.add(action)
        result = self.actions.execute(action)
        entry = {"action": result.action, "success": result.success, "detail": result.detail,
                 "t": round(now - inc.opened_at, 1)}
        inc.actions.append(entry)
        inc.note(now, "action", **entry)
        self._record(f"action:{action.value}", {"incident_id": inc.id, **entry})
        log.info("Action %s : %s (%s)", action.value, "OK" if result.success else "ÉCHEC", result.detail)

        if not result.success:
            inc.failed_repairs += 1
            return result
        if action == Action.DEGRADED_MODE:
            inc.degraded = True
        if action == Action.ROLLBACK_MODEL:
            self.collector.trust_next_model_change()  # la version restaurée n'est pas une promotion suspecte
        if action in RESTART_ACTIONS and inc.degraded:
            inc.reapply_degraded = True
        if verify:
            inc.pending = (action, now)
        return result

    # ------------------------------------------------------------ clôture
    def _resolve(self, now: float) -> None:
        inc = self.incident
        if inc.degraded:
            result = self.actions.exit_degraded_mode()
            inc.note(now, "degraded_mode_off", success=result.success)
        inc.note(now, "resolved")
        report = self._report(inc, now)
        log.info("Incident %s résolu en %.0f s", inc.id, report["duration_seconds"])
        self._publish(EventType.INCIDENT_RESOLVED, Severity.INFO, report)
        self._record("incident_resolved", report)
        self.closed_at.append(now)
        self.incident, self.ok_streak = None, 0

    # ------------------------------------------------------------ outils
    def _notify_human(self, now: float, reason: str) -> None:
        inc = self.incident
        inc.human_notified_at = now
        inc.note(now, "human_notified", reason=reason)
        log.warning("Incident %s : humain prévenu (%s)", inc.id, reason)
        self._record("human_notified", {"incident_id": inc.id, "level": inc.level.value, "reason": reason})
        self._publish(EventType.APPROVAL_REQUESTED, Severity.CRITICAL,
                      {**self._report(inc, now), "reason": reason})

    def _context(self, diag: Diagnosis, inc: Incident | None, now: float) -> IncidentContext:
        while self.closed_at and now - self.closed_at[0] > 3600:
            self.closed_at.popleft()
        return IncidentContext(
            duration_seconds=0.0 if inc is None else now - inc.opened_at,
            component=diag.component,
            incidents_last_hour=len(self.closed_at),
            failed_repairs=0 if inc is None else inc.failed_repairs,
        )

    @staticmethod
    def _summary(inc: Incident, window: WindowStats, probes: ProbeResult) -> dict:
        return {
            "incident_id": inc.id,
            "cause": inc.diagnosis.cause.value,
            "component": inc.diagnosis.component,
            "level": inc.level.value,
            "score": inc.severity.score,
            "evidence": list(inc.diagnosis.evidence),
            "error_rate": round(window.error_rate, 4),
            "p95_latency": window.p95_latency,
            "probe_failure_rate": round(probes.failure_rate, 4),
            "model_version": window.model_version,
        }

    @staticmethod
    def _report(inc: Incident, now: float) -> dict:
        """Post-mortem : ce qui s'est passé, ce qui a été tenté, combien de temps."""
        return {
            "incident_id": inc.id,
            "cause": inc.diagnosis.cause.value,
            "component": inc.diagnosis.component,
            "level": inc.level.value,
            "score": inc.severity.score,
            "breakdown": inc.severity.breakdown,
            "evidence": list(inc.diagnosis.evidence),
            "actions": inc.actions,
            "failed_repairs": inc.failed_repairs,
            "degraded": inc.degraded,
            "duration_seconds": round(now - inc.opened_at, 1),
            "timeline": inc.timeline,
        }

    def _publish(self, type_: EventType, severity: Severity, payload: dict) -> None:
        try:
            self.bus.publish(Event(type=type_, source=AGENT_NAME, severity=severity, payload=payload))
        except Exception as exc:  # Redis en panne : on journalise mais on continue
            log.error("Publication %s impossible : %s", type_.value, exc)

    def _record(self, action: str, details: dict) -> None:
        try:
            self.action_log.record(AGENT_NAME, action, model=config.MODEL_NAME, details=details)
        except Exception as exc:  # Postgres en panne : idem
            log.error("Écriture du journal impossible : %s", exc)
