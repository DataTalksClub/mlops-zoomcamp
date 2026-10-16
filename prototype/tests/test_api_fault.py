import pytest

from common import config
from pipeline.api import app as api

PAYLOAD = {"PULocationID": 43, "DOLocationID": 151, "trip_distance": 2.0}


class OkModel:
    def predict(self, X):
        return [9.0]


@pytest.fixture(autouse=True)
def clean_state(monkeypatch):
    monkeypatch.setattr(api, "load_model", lambda: None)
    monkeypatch.setattr(config, "FAULT_INJECTION", True)
    api.state.update(model=OkModel(), version="5")
    yield
    api.state.update(model=None, version=None, error=None, degraded=False,
                     fault={"mode": "none", "rate": 0.0, "seconds": 0.0})
    api.DEGRADED_MODE.set(0)


def test_injected_errors():
    client = api.app.test_client()
    client.post("/fault", json={"mode": "errors", "rate": 1.0})
    assert client.post("/predict", json=PAYLOAD).status_code == 500


def test_injected_latency():
    client = api.app.test_client()
    client.post("/fault", json={"mode": "latency", "seconds": 0.05})
    resp = client.post("/predict", json=PAYLOAD)
    assert resp.status_code == 200


def test_recover_with_mode_none():
    client = api.app.test_client()
    client.post("/fault", json={"mode": "errors", "rate": 1.0})
    client.post("/fault", json={"mode": "none"})
    assert client.post("/predict", json=PAYLOAD).status_code == 200


def test_degraded_mode_is_not_affected_by_injected_faults():
    client = api.app.test_client()
    client.post("/fault", json={"mode": "errors", "rate": 1.0})
    client.post("/degraded", json={"enabled": True})
    assert client.post("/predict", json=PAYLOAD).status_code == 200                       # utilisateurs : secours
    assert client.post("/predict", json=PAYLOAD,
                       headers={"X-Bypass-Degraded": "1"}).status_code == 500             # sondes : vraie panne


def test_fault_endpoint_is_disabled_by_default(monkeypatch):
    monkeypatch.setattr(config, "FAULT_INJECTION", False)
    client = api.app.test_client()
    assert client.post("/fault", json={"mode": "errors"}).status_code == 404


def test_unknown_mode_is_rejected():
    client = api.app.test_client()
    assert client.post("/fault", json={"mode": "chaos"}).status_code == 400
