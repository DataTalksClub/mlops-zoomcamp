"""Gravité d'un incident : score déterministe sur 12 points, puis niveau.

6 critères notés de 0 à 2 (erreurs, latence, budget SLO, durée, composant,
historique). Certains cas passent en critique d'office. Le calcul est fait
par le code, jamais par le LLM ; les seuils sont dans common/config.py."""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass

from agents.reliability.metrics import WindowStats
from common import config
from common.events import Severity

COMPONENT_POINTS = {"api": 0, "redis": 1, "mlflow": 2, "postgres": 2}
_LEVELS = [Severity.INFO, Severity.WARNING, Severity.CRITICAL]


@dataclass(frozen=True)
class IncidentContext:
    """Ce que l'agent sait de l'incident en cours (hors métriques)."""
    duration_seconds: float = 0.0
    component: str = "api"            # composant touché, fourni par le diagnostic
    incidents_last_hour: int = 0      # incidents précédents dans l'heure (hors celui-ci)
    failed_repairs: int = 0           # tentatives de réparation déjà échouées
    snapshot_possible: bool = True    # peut-on revenir en arrière si une action échoue ?


@dataclass(frozen=True)
class SeverityResult:
    score: int                        # 0 à 12
    level: Severity
    breakdown: dict[str, int]         # points par critère (pour le rapport et le juge)
    forced_reason: str | None = None  # raison d'un passage en critique d'office


class ErrorBudget:
    """Budget d'erreurs du SLO sur une fenêtre glissante.

    Avec un SLO à 99 %, on a droit à 1 % d'échecs. consumed() renvoie la part
    de ce droit déjà utilisée (0.5 = 50 % du budget brûlé)."""

    def __init__(self, target: float | None = None, window_seconds: float | None = None):
        self.target = config.SLO_TARGET if target is None else target
        self.window_seconds = config.SLO_WINDOW_MINUTES * 60 if window_seconds is None else window_seconds
        self._history: deque[tuple[float, float, float]] = deque()  # (instant, requêtes, erreurs)

    def add(self, window: WindowStats, now: float | None = None) -> None:
        now = time.time() if now is None else now
        if window.reachable:
            self._history.append((now, window.requests, window.errors))
        else:  # API injoignable : nombre de requêtes inconnu, on compte un lot entièrement en échec
            self._history.append((now, config.MIN_REQUESTS, config.MIN_REQUESTS))
        while self._history and now - self._history[0][0] > self.window_seconds:
            self._history.popleft()

    def consumed(self) -> float:
        requests = sum(r for _, r, _ in self._history)
        errors = sum(e for _, _, e in self._history)
        allowed = max((1 - self.target) * requests, 1.0)  # au moins 1 erreur tolérée
        return errors / allowed


def is_breach(window: WindowStats) -> bool:
    """La fenêtre dépasse-t-elle un seuil ? (l'agent ouvre un incident après 2 dépassements de suite)"""
    if not window.reachable:
        return True
    if window.requests >= config.MIN_REQUESTS and window.error_rate > config.MAX_ERROR_RATE:
        return True
    return window.p95_latency is not None and window.p95_latency > config.MAX_LATENCY_SECONDS


def _points(value: float | None, medium: float, high: float) -> int:
    if value is None:
        return 0
    if value > high:
        return 2
    if value > medium:
        return 1
    return 0


def _forced_critical(window: WindowStats, ctx: IncidentContext, significant: bool) -> str | None:
    if not window.reachable:
        return "API injoignable"
    if significant and window.error_rate > config.CRITICAL_ERROR_RATE:
        return f"plus de {config.CRITICAL_ERROR_RATE:.0%} d'erreurs"
    if ctx.component == "postgres":
        return "Postgres touché (risque sur les données)"
    if not ctx.snapshot_possible:
        return "snapshot impossible : aucune action réversible"
    return None


def compute_severity(window: WindowStats, budget_consumed: float, ctx: IncidentContext) -> SeverityResult:
    # Avec trop peu de requêtes, 1 erreur sur 2 ferait 50 % : le taux n'est pas significatif.
    significant = (not window.reachable) or window.requests >= config.MIN_REQUESTS
    if ctx.failed_repairs > 0 or ctx.incidents_last_hour >= 2:
        history = 2
    else:
        history = 1 if ctx.incidents_last_hour == 1 else 0

    breakdown = {
        "error_rate": _points(window.error_rate, config.MAX_ERROR_RATE, config.HIGH_ERROR_RATE) if significant else 0,
        "latency": _points(window.p95_latency, config.MAX_LATENCY_SECONDS, config.HIGH_LATENCY_SECONDS),
        "error_budget": _points(budget_consumed, 0.25, 0.50),
        "duration": _points(ctx.duration_seconds, 120, 600),       # 2 min / 10 min
        "component": COMPONENT_POINTS.get(ctx.component, 1),       # composant inconnu : prudence
        "history": history,
    }
    score = sum(breakdown.values())
    forced = _forced_critical(window, ctx, significant)

    if forced or score >= config.SEVERITY_HIGH_SCORE:
        level = Severity.CRITICAL
    elif score >= config.SEVERITY_MEDIUM_SCORE:
        level = Severity.WARNING
    else:
        level = Severity.INFO
    return SeverityResult(score=score, level=level, breakdown=breakdown, forced_reason=forced)


def escalate(current: Severity | None, new: Severity) -> Severity:
    """Pendant un incident, le niveau ne peut que monter."""
    if current is None:
        return new
    return max(current, new, key=_LEVELS.index)