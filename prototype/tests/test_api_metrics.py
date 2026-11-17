from prometheus_client.parser import text_string_to_metric_families

from pipeline.api import app as api

PAYLOAD = {"PULocationID": 43, "DOLocationID": 151, "trip_distance": 1.8}


class FakeModel:
    def predict(self, X):
        return [12.5]


class BrokenModel:
    def predict(self, X):
        raise RuntimeError("modèle cassé")


def sample(client, name, **labels) -> float:
    """Valeur d'une série dans /metrics (0 si absente)."""
    text = client.get("/metrics").get_data(as_text=True)
    for family in text_string_to_metric_families(text):
        for s in family.samples:
            if s.name == name and all(s.labels.get(k) == v for k, v in labels.items()):
                return s.value
    return 0.0


def test_metrics_count_status_codes_and_latency(monkeypatch):
    client = api.app.test_client()
    monkeypatch.setattr(api, "load_model", lambda: None)  # pas de MLflow dans ce test

    # Registre global partagé entre tests : on compare des deltas.
    ok0 = sample(client, "api_requests_total", endpoint="/predict", status="200")
    no_model0 = sample(client, "api_requests_total", endpoint="/predict", status="503")
    crash0 = sample(client, "api_requests_total", endpoint="/predict", status="500")
    lat0 = sample(client, "api_request_latency_seconds_count", endpoint="/predict")

    api.state.update(model=FakeModel(), version="7", error=None)
    assert client.post("/predict", json=PAYLOAD).status_code == 200

    api.state.update(model=None, version=None, error="test")
    assert client.post("/predict", json=PAYLOAD).status_code == 503

    api.state.update(model=BrokenModel(), version="8", error=None)
    assert client.post("/predict", json=PAYLOAD).status_code == 500

    assert sample(client, "api_requests_total", endpoint="/predict", status="200") == ok0 + 1
    assert sample(client, "api_requests_total", endpoint="/predict", status="503") == no_model0 + 1
    assert sample(client, "api_requests_total", endpoint="/predict", status="500") == crash0 + 1
    assert sample(client, "api_request_latency_seconds_count", endpoint="/predict") == lat0 + 3

    api.state.update(model=None, version=None, error=None)


def test_metrics_endpoint_is_not_self_counted():
    client = api.app.test_client()
    client.get("/metrics")
    client.get("/metrics")
    assert sample(client, "api_requests_total", endpoint="/metrics") == 0