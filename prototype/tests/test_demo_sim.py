"""Tests de la simulation utilisée par la démo Streamlit."""
from datetime import datetime

import pytest

from agents.cost.settings import CostConfig
from demo.sim import Simulation

NOW = datetime(2026, 10, 12, 14, 0)


def make_sim(budget=20.0):
    cfg = CostConfig(cost_per_cpu_second=0.01, spot_discount=0.6,
                     monthly_budget=budget,
                     default_cpu_seconds_per_month_of_data=300.0)
    return Simulation(cfg, clock=lambda: NOW)


def types(sim):
    return [e["type"] for e in sim.bus.events]


def test_request_under_budget_launches_automatically():
    sim = make_sim(budget=100.0)
    answer = sim.request_retrain("taxi", 1, "ds")  # 300 s x 0.01 = 3.0
    assert answer["exceeds_budget"] is False
    assert sim.pending is None
    assert sim.month_total() == pytest.approx(3.0)
    assert "retrain_started" in [r["action"] for r in sim.log.rows]


def test_request_over_budget_waits_for_approval():
    sim = make_sim(budget=20.0)
    sim.add_training("taxi", 1800.0, 1)               # 18.0 déjà dépensés
    answer = sim.request_retrain("taxi", 3, "ds")     # 1800 s/mois x 3 x 0.01 = 54
    assert answer["exceeds_budget"] is True
    assert "budget_exceeded" in types(sim)
    assert sim.pending is not None
    assert sim.month_total() == pytest.approx(18.0)   # rien lancé tant que pas approuvé


def test_approve_launches_and_clears_pending():
    sim = make_sim(budget=20.0)
    sim.add_training("taxi", 1800.0, 1)
    sim.request_retrain("taxi", 3, "ds")
    sim.approve()
    assert sim.pending is None
    actions = [r["action"] for r in sim.log.rows]
    assert "approved" in actions and "retrain_started" in actions
    assert sim.month_total() > 18.0


def test_refuse_clears_pending_without_cost():
    sim = make_sim(budget=20.0)
    sim.add_training("taxi", 1800.0, 1)
    sim.request_retrain("taxi", 3, "ds")
    before = sim.month_total()
    sim.refuse()
    assert sim.pending is None
    assert sim.month_total() == pytest.approx(before)
    assert "refused" in [r["action"] for r in sim.log.rows]
    assert "retrain_started" not in [r["action"] for r in sim.log.rows]


def test_approve_and_refuse_without_pending_do_nothing():
    sim = make_sim()
    sim.approve()
    sim.refuse()
    assert sim.log.rows == []


def test_advance_api_cpu_bills_the_delta():
    sim = make_sim()
    assert sim.advance_api_cpu("taxi", 60.0) == pytest.approx(0.6)
    assert sim.advance_api_cpu("taxi", 40.0) == pytest.approx(0.4)
    assert sim.month_total() == pytest.approx(1.0)


def test_budget_ratio_is_capped_at_one():
    sim = make_sim(budget=10.0)
    sim.add_training("taxi", 5000.0, 1)  # 50 > 10
    assert sim.budget_ratio() == 1.0
