import pytest

from common import config
from pipeline.api import app as api

PAYLOAD = {"PULocationID": 43, "DOLocationID": 151, "trip_distance": 2.0}


class BrokenModel:
    def predict(self, X):
        raise RuntimeError("modèle cassé")


@pytest.fixture(autouse=True)
def clean_state(monkeypatch):
    """L'état de l'API est global : on le remet à zéro après chaque test."""
    monkeypatch.setattr(api, "load_model", lambda: None)
    monkeypatch.setattr(config, "FALLBACK_BASE_MINUTES", 4.0)
    monkeypatch.setattr(config, "FALLBACK_MINUTES_PER_MILE", 3.5)
    yield
    api.state.update(model=None, version=None, error=None, degraded=False)
    api.DEGRADED_MODE.set(0)


def test_degraded_mode_serves_fallback_even_if_model_is_broken():
    client = api.app.test_client()
    api.state.update(model=BrokenModel(), version="5")
    assert client.post("/degraded", json={"enabled": True}).get_json() == {"degraded": True}

    resp = client.post("/predict", json=PAYLOAD)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["degraded"] is True
    assert body["model_version"] == "fallback"
    assert body["duration"] == pytest.approx(11.0)   # 4 + 3.5 x 2


def test_probe_bypasses_degraded_mode_and_sees_the_real_model():
    client = api.app.test_client()
    api.state.update(model=BrokenModel(), version="5")
    client.post("/degraded", json={"enabled": True})
    resp = client.post("/predict", json=PAYLOAD, headers={"X-Bypass-Degraded": "1"})
    assert resp.status_code == 500  # le vrai modèle est toujours cassé : l'agent le voit


def test_health_reports_degraded_flag():
    client = api.app.test_client()
    client.post("/degraded", json={"enabled": True})
    assert client.get("/health").get_json()["degraded"] is True


def test_invalid_body_is_rejected():
    client = api.app.test_client()
    assert client.post("/degraded", json={"enabled": "oui"}).status_code == 400
    assert client.post("/degraded").status_code == 400


def test_disabling_returns_to_the_real_model():
    class OkModel:
        def predict(self, X):
            return [9.0]

    client = api.app.test_client()
    api.state.update(model=OkModel(), version="5")
    client.post("/degraded", json={"enabled": True})
    client.post("/degraded", json={"enabled": False})
    body = client.post("/predict", json=PAYLOAD).get_json()
    assert body == {"duration": 9.0, "model_version": "5", "degraded": False}