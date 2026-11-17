from agents.reliability.catalog import CATALOG, LOW_RISK_ACTIONS, Action
from agents.reliability.diagnosis import Cause, Signals, diagnose
from agents.reliability.metrics import WindowStats


def win(rate=0.0, p95=0.05, requests=100, reachable=True, model_loaded=True):
    return WindowStats(duration=15, reachable=reachable, requests=requests, errors=round(rate * requests),
                       error_rate=rate if reachable else 1.0, p95_latency=p95, model_loaded=model_loaded,
                       model_version=4, health_ok=True, counter_reset=False)


def test_crash_loop_does_not_simply_restart():
    d = diagnose(win(reachable=False), Signals(container_status="restarting", restarts_recent=4))
    assert d.cause == Cause.CRASH_LOOP
    assert Action.RESTART_API not in d.playbook


def test_stopped_container():
    d = diagnose(win(reachable=False), Signals(container_status="exited"))
    assert d.cause == Cause.API_DOWN
    assert d.playbook[0] == Action.RESTART_API


def test_running_but_unresponsive_api():
    d = diagnose(win(reachable=False), Signals(container_status="running"))
    assert d.cause == Cause.API_UNRESPONSIVE


def test_postgres_down_goes_straight_to_humans():
    d = diagnose(win(rate=0.10), Signals(postgres_ok=False))
    assert d.cause == Cause.POSTGRES_DOWN
    assert d.component == "postgres"
    assert d.playbook == (Action.ESCALATE,)


def test_mlflow_down_never_restarts_api_nor_rolls_back():
    d = diagnose(win(rate=0.10), Signals(mlflow_ok=False))
    assert d.cause == Cause.MLFLOW_DOWN
    assert Action.RESTART_API not in d.playbook
    assert Action.ROLLBACK_MODEL not in d.playbook


def test_resource_exhaustion():
    d = diagnose(win(p95=2.0), Signals(memory_percent=95))
    assert d.cause == Cause.RESOURCE_EXHAUSTION


def test_no_model_loaded():
    d = diagnose(win(rate=1.0, model_loaded=False), Signals())
    assert d.cause == Cause.MODEL_UNAVAILABLE
    assert d.playbook[0] == Action.RELOAD_MODEL


def test_errors_right_after_a_promotion_point_to_the_model():
    d = diagnose(win(rate=0.30), Signals(model_age_seconds=5 * 60))
    assert d.cause == Cause.BAD_MODEL
    assert d.playbook[0] == Action.ROLLBACK_MODEL


def test_same_errors_with_an_old_model_are_unknown():
    d = diagnose(win(rate=0.30), Signals(model_age_seconds=3 * 3600))
    assert d.cause == Cause.UNKNOWN
    assert d.playbook[-1] == Action.ESCALATE


def test_slow_without_errors_is_overload():
    d = diagnose(win(p95=2.5), Signals())
    assert d.cause == Cause.OVERLOAD


def test_infrastructure_has_priority_over_model():
    d = diagnose(win(reachable=False), Signals(container_status="exited", model_age_seconds=60))
    assert d.cause == Cause.API_DOWN


def test_every_playbook_ends_with_escalation_and_uses_known_actions():
    cases = [
        (win(reachable=False), Signals(container_status="exited")),
        (win(rate=0.1), Signals(mlflow_ok=False)),
        (win(rate=0.3), Signals(model_age_seconds=60)),
        (win(rate=0.3), Signals()),
    ]
    for window, signals in cases:
        d = diagnose(window, signals)
        assert d.playbook[-1] == Action.ESCALATE
        assert all(a in CATALOG for a in d.playbook)
        assert d.evidence


def test_rollback_is_not_a_low_risk_action():
    assert Action.ROLLBACK_MODEL not in LOW_RISK_ACTIONS
    assert Action.RESTART_API in LOW_RISK_ACTIONS