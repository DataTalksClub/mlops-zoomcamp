import numpy as np
import pytest
from mlflow import MlflowClient

from agents.retrain.agent import RetrainAgent, default_months, parse_period
from common import config
from common.action_log import ActionLog
from common.events import Event, EventType
from tests.conftest import synthetic_month


class FakeBus:
    """Garde les événements publiés au lieu de les envoyer sur Redis."""

    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)


def reader(corrupted=()):
    """Données synthétiques ; les mois de `corrupted` ont des durées mélangées (données cassées)."""
    def read(year, month):
        df = synthetic_month(year, month)
        if (year, month) in corrupted:
            df["duration"] = np.random.default_rng(0).permutation(df["duration"].values)
        return df
    return read


def request(period=None, **extra):
    return Event(type=EventType.RETRAIN_REQUESTED, source="orchestrateur", payload={"period": period, **extra})


@pytest.fixture
def make_agent(local_mlflow, tmp_path):
    def make(corrupted=(), cooldown=0):
        return RetrainAgent(bus=FakeBus(), log=ActionLog(url=f"sqlite:///{tmp_path / 'log.db'}"),
                            read_data=reader(corrupted), reload=lambda: True,
                            list_months=lambda: [(2023, 1), (2023, 2), (2023, 3)], cooldown_minutes=cooldown)
    return make


def aliases(version):
    return set(MlflowClient(config.MLFLOW_TRACKING_URI).get_model_version(config.MODEL_NAME, version).aliases)


def test_parse_period():
    assert parse_period("2023-02") == [(2023, 2)]
    assert parse_period({"start": "2022-11", "end": "2023-01"}) == [(2022, 11), (2022, 12), (2023, 1)]


def test_better_challenger_is_promoted_and_old_version_kept(make_agent):
    agent = make_agent(corrupted={(2023, 1)})
    first = agent.handle(request("2023-01"))  # aucun modèle en production : promu directement
    assert first["decision"] == "promoted"

    second = agent.handle(request("2023-02"))  # données propres : nettement meilleur
    assert second["decision"] == "promoted"
    assert second["challenger_rmse"] < second["production_rmse"]
    assert "production" in aliases(second["challenger_version"])
    assert "previous" in aliases(first["challenger_version"])  # pour un rollback
    assert [e.type for e in agent.bus.events][-2:] == [EventType.MODEL_REGISTERED, EventType.MODEL_PROMOTED]
    assert agent.log.latest()[0]["action"] == "model_promoted"


def test_worse_challenger_is_blocked_and_production_unchanged(make_agent):
    agent = make_agent(corrupted={(2023, 2)})
    first = agent.handle(request("2023-01"))
    second = agent.handle(request("2023-02"))  # entraîné sur des données cassées

    assert second["decision"] == "blocked"
    assert second["challenger_rmse"] > second["production_rmse"]
    assert "production" in aliases(first["challenger_version"])
    assert "production" not in aliases(second["challenger_version"])
    blocked = agent.bus.events[-1]
    assert blocked.type == EventType.PROMOTION_BLOCKED
    assert {"challenger_rmse", "production_rmse"} <= blocked.payload.keys()


def test_default_months():
    available = [(2023, 1), (2023, 2), (2023, 3)]
    assert default_months(available, 1) == [(2023, 2)]  # mars sert de test
    assert default_months(available, 2) == [(2023, 1), (2023, 2)]


def test_without_period_uses_latest_months(make_agent):
    agent = make_agent()
    agent.handle(request())
    registered = next(e for e in agent.bus.events if e.type == EventType.MODEL_REGISTERED)
    assert registered.payload["period"] == ["2023-02"]


def test_duplicates_and_cooldown_are_skipped(make_agent):
    agent = make_agent(cooldown=60)
    assert agent.handle(request("2023-01"))["decision"] == "promoted"

    assert agent.handle(request("2023-01"))["decision"] == "skipped"  # même période
    assert agent.handle(request("2023-02"))["decision"] == "skipped"  # moins de 60 min
    assert agent.log.latest()[0]["action"] == "retrain_skipped"

    validated = agent.handle(request("2023-02", approved_by="responsable"))  # validé par un humain
    assert validated["decision"] != "skipped"