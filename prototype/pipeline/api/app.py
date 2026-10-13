"""API de prédiction : charge le modèle "taxi-duration" qui porte l'alias production.

Routes :
    POST /predict  {"PULocationID": 43, "DOLocationID": 151, "trip_distance": 1.8}
    GET  /health   état de l'API et version du modèle chargé
    POST /reload   recharge le modèle en production (après une promotion ou un rollback)
    GET  /metrics  métriques Prometheus (lues par l'agent Fiabilité)
    POST /degraded  active/désactive le mode dégradé (agent Fiabilité)"""

from __future__ import annotations

import time

import mlflow
from flask import Flask, Response, g, jsonify, request
from mlflow import MlflowClient
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

from common import config
from pipeline.data import prepare_features

app = Flask("duration-prediction")
state = {"model": None, "version": None, "error": None, "degraded": False}
BYPASS_HEADER = "X-Bypass-Degraded"  # les sondes de l'agent testent le vrai modèle même en mode dégradé

# --- Métriques (agent Fiabilité) ---
REQUESTS = Counter("api_requests_total", "Requêtes HTTP traitées", ["endpoint", "status"])
LATENCY = Histogram(
    "api_request_latency_seconds", "Temps de traitement des requêtes", ["endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)
MODEL_LOADED = Gauge("api_model_loaded", "1 si un modèle est chargé, 0 sinon")
MODEL_VERSION = Gauge("api_model_version", "Version MLflow du modèle servi (0 si aucun)")
DEGRADED_MODE = Gauge("api_degraded_mode", "1 si l'API sert le modèle de secours")
FALLBACK_PREDICTIONS = Counter("api_fallback_predictions_total", "Prédictions servies par le modèle de secours")

@app.before_request
def _start_timer() -> None:
    g.start = time.perf_counter()


@app.after_request
def _record_metrics(response: Response) -> Response:
    # url_rule.rule = route déclarée ("/predict"), pas l'URL brute : évite une
    # explosion du nombre de séries si on reçoit des URL arbitraires (404).
    endpoint = request.url_rule.rule if request.url_rule else "unmatched"
    if endpoint != "/metrics":  # on ne mesure pas le scraping lui-même
        LATENCY.labels(endpoint).observe(time.perf_counter() - g.get("start", time.perf_counter()))
        REQUESTS.labels(endpoint, str(response.status_code)).inc()
    return response

def load_model() -> None:
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    try:
        mv = MlflowClient().get_model_version_by_alias(config.MODEL_NAME, config.PRODUCTION_ALIAS)
        state["model"] = mlflow.sklearn.load_model(f"models:/{config.MODEL_NAME}@{config.PRODUCTION_ALIAS}")
        state["version"] = mv.version
        state["error"] = None
        MODEL_LOADED.set(1)
        MODEL_VERSION.set(int(mv.version))
    except Exception as exc:  # pas encore de modèle, ou MLflow indisponible
        state["error"] = str(exc)
        if state["model"] is None:
            MODEL_LOADED.set(0)
            MODEL_VERSION.set(0)

def fallback_duration(ride: dict) -> float:
    """Modèle de secours : estimation simple, toujours disponible, sans MLflow."""
    return config.FALLBACK_BASE_MINUTES + config.FALLBACK_MINUTES_PER_MILE * float(ride["trip_distance"])

@app.post("/predict")
def predict():
    ride = request.get_json()
    if state["degraded"] and request.headers.get(BYPASS_HEADER) != "1":
        FALLBACK_PREDICTIONS.inc()
        return jsonify({"duration": fallback_duration(ride), "model_version": "fallback", "degraded": True})
    if state["model"] is None:
        load_model()
    if state["model"] is None:
        return jsonify({"error": "aucun modèle en production", "detail": state["error"]}), 503
    duration = float(state["model"].predict([prepare_features(ride)])[0])
    return jsonify({"duration": duration, "model_version": state["version"], "degraded": False})


@app.get("/health")
def health():
    if state["model"] is None:
        load_model()
    ok = state["model"] is not None
    return jsonify({"status": "ok" if ok else "no_model", "model_version": state["version"],
                    "degraded": state["degraded"]}), 200 if ok else 503

@app.post("/reload")
def reload_model():
    load_model()
    return health()

@app.post("/degraded")
def set_degraded():
    body = request.get_json(silent=True) or {}
    if not isinstance(body.get("enabled"), bool):
        return jsonify({"error": 'corps attendu : {"enabled": true} ou {"enabled": false}'}), 400
    state["degraded"] = body["enabled"]
    DEGRADED_MODE.set(1 if state["degraded"] else 0)
    return jsonify({"degraded": state["degraded"]})

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9696)