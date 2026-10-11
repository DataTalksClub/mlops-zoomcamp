"""API de prédiction : charge le modèle "taxi-duration" qui porte l'alias production.

Routes :
    POST /predict  {"PULocationID": 43, "DOLocationID": 151, "trip_distance": 1.8}
    GET  /health   état de l'API et version du modèle chargé
    POST /reload   recharge le modèle en production (après une promotion ou un rollback)"""
from __future__ import annotations

import mlflow
from flask import Flask, jsonify, request
from mlflow import MlflowClient

from common import config
from pipeline.data import prepare_features

app = Flask("duration-prediction")
state = {"model": None, "version": None, "error": None}


def load_model() -> None:
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    try:
        mv = MlflowClient().get_model_version_by_alias(config.MODEL_NAME, config.PRODUCTION_ALIAS)
        state["model"] = mlflow.sklearn.load_model(f"models:/{config.MODEL_NAME}@{config.PRODUCTION_ALIAS}")
        state["version"] = mv.version
        state["error"] = None
    except Exception as exc:  # pas encore de modèle, ou MLflow indisponible
        state["error"] = str(exc)


@app.post("/predict")
def predict():
    if state["model"] is None:
        load_model()
    if state["model"] is None:
        return jsonify({"error": "aucun modèle en production", "detail": state["error"]}), 503
    features = prepare_features(request.get_json())
    duration = float(state["model"].predict([features])[0])
    return jsonify({"duration": duration, "model_version": state["version"]})


@app.get("/health")
def health():
    if state["model"] is None:
        load_model()
    ok = state["model"] is not None
    return jsonify({"status": "ok" if ok else "no_model", "model_version": state["version"]}), 200 if ok else 503


@app.post("/reload")
def reload_model():
    load_model()
    return health()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9696)