import pytest
from agents.reliability.metrics import WindowStats
from agents.reliability.severity import (
    ErrorBudget, IncidentContext, compute_severity, escalate, is_breach,
)
from common.events import Severity


def win(rate=0.0, p95=0.05, requests=100, reachable=True):
    return WindowStats(duration=15, reachable=reachable, requests=requests, errors=round(rate * requests),
                       error_rate=rate if reachable else 1.0, p95_latency=p95, model_loaded=True,
                       model_version=3, health_ok=True, counter_reset=False)


def test_low_level_example_from_the_plan():
    # 12 % d'erreurs (1) + budget 30 % (1) + 3 min (1) = 3 -> faible
    r = compute_severity(win(rate=0.12), 0.30, IncidentContext(duration_seconds=180))
    assert r.score == 3
    assert r.level == Severity.INFO


def test_medium_level():
    # 12 % (1) + budget 60 % (2) + 11 min (2) = 5 -> moyen
    r = compute_severity(win(rate=0.12), 0.60, IncidentContext(duration_seconds=660))
    assert r.score == 5
    assert r.level == Severity.WARNING
    assert r.breakdown["error_budget"] == 2


def test_high_level_by_score():
    # 30 % (2) + p95 4 s (2) + budget 60 % (2) + 11 min (2) = 8 -> élevé
    r = compute_severity(win(rate=0.30, p95=4.0), 0.60, IncidentContext(duration_seconds=660))
    assert r.score == 8
    assert r.level == Severity.CRITICAL
    assert r.forced_reason is None


def test_unreachable_api_is_critical_whatever_the_score():
    r = compute_severity(win(reachable=False), 0.0, IncidentContext())
    assert r.level == Severity.CRITICAL
    assert "injoignable" in r.forced_reason


def test_postgres_is_critical():
    r = compute_severity(win(rate=0.06), 0.0, IncidentContext(component="postgres"))
    assert r.level == Severity.CRITICAL


def test_failed_repair_raises_history_points():
    r = compute_severity(win(), 0.0, IncidentContext(failed_repairs=1))
    assert r.breakdown["history"] == 2


def test_low_traffic_error_rate_is_not_significant():
    r = compute_severity(win(rate=0.66, requests=3), 0.0, IncidentContext())
    assert r.breakdown["error_rate"] == 0
    assert r.level == Severity.INFO
    assert not is_breach(win(rate=0.66, requests=3))


def test_breach_detection():
    assert is_breach(win(rate=0.10))
    assert is_breach(win(p95=1.5))
    assert is_breach(win(reachable=False))
    assert not is_breach(win(rate=0.02, p95=0.2))


def test_level_never_goes_down_during_an_incident():
    assert escalate(Severity.WARNING, Severity.INFO) == Severity.WARNING
    assert escalate(Severity.WARNING, Severity.CRITICAL) == Severity.CRITICAL
    assert escalate(None, Severity.INFO) == Severity.INFO


def test_error_budget_consumption_and_sliding_window():
    budget = ErrorBudget(target=0.99, window_seconds=3600)
    budget.add(win(rate=0.005, requests=1000), now=0)      # 5 erreurs, 10 autorisées
    assert budget.consumed() == pytest.approx(0.5)
    budget.add(win(rate=0.0, requests=1000), now=4000)     # 1 h plus tard : les vieilles erreurs sortent
    assert budget.consumed() == 0.0