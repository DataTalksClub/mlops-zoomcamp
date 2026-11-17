from pipeline import train as train_module
from pipeline.api import app as api


def test_first_model_goes_to_production_then_api_serves_it(local_mlflow):
    first = train_module.train(2023, 1)
    assert first["promoted"] is True

    second = train_module.train(2023, 2)
    assert second["promoted"] is False  # un challenger n'est pas promu tout seul

    api.state.update(model=None, version=None, error=None)
    client = api.app.test_client()
    assert client.get("/health").get_json()["model_version"] == first["version"]

    resp = client.post("/predict", json={"PULocationID": 43, "DOLocationID": 151, "trip_distance": 1.8})
    assert resp.status_code == 200
    assert resp.get_json()["duration"] > 0