"""Banc de pannes pour tester et démontrer l'agent Fiabilité.

À lancer depuis prototype/ (venv activé, stack Docker démarrée, agent lancé
dans un autre terminal). Chaque panne indique la réaction attendue de l'agent.

    python -m scripts.inject_failure traffic       # trafic utilisateur simulé (Ctrl+C pour arrêter)
    python -m scripts.inject_failure crash         # arrête l'API
    python -m scripts.inject_failure errors        # 30 % d'erreurs 500 (option --rate)
    python -m scripts.inject_failure latency       # +2 s par prédiction (option --seconds)
    python -m scripts.inject_failure bad-model     # promeut un modèle cassé
    python -m scripts.inject_failure mlflow-down   # arrête MLflow puis redémarre l'API
    python -m scripts.inject_failure recover       # annule les pannes (le geste de l'humain)
"""
from __future__ import annotations

import argparse
import random
import time

import requests

from common import config

EXPECTED = {
    "crash": "incident critique (api_down) -> humain prévenu -> redémarrage -> résolu",
    "errors": "incident (cause inconnue) -> redémarrage (efface la panne en mémoire) -> résolu",
    "latency": "incident (overload) -> mode dégradé -> escalade ; puis `recover` -> résolu",
    "bad-model": "incident critique (bad_model) -> mode dégradé -> rollback vers la version précédente -> résolu",
    "mlflow-down": "incident critique (mlflow_down) -> mode dégradé, ni redémarrage ni rollback -> escalade ; "
                   "puis `recover` -> résolu",
}


def _docker():
    import docker
    return docker.from_env()


def _set_fault(mode: str, **params) -> None:
    resp = requests.post(f"{config.API_URL}/fault", json={"mode": mode, **params}, timeout=5)
    if resp.status_code == 404:
        raise SystemExit("Injection désactivée : ajouter FAULT_INJECTION: \"1\" au service api "
                         "dans docker-compose.yml, puis `docker compose up -d api`.")
    resp.raise_for_status()
    print(f"Panne injectée dans l'API : {resp.json()}")


def crash() -> None:
    _docker().containers.get(config.API_CONTAINER_NAME).stop()
    print(f"Conteneur {config.API_CONTAINER_NAME} arrêté.")


def errors(rate: float) -> None:
    _set_fault("errors", rate=rate)


def latency(seconds: float) -> None:
    _set_fault("latency", seconds=seconds)


def bad_model() -> None:
    """Enregistre un modèle qui plante à chaque prédiction et le met en production,
    comme le ferait une promotion ratée. L'ancienne version reçoit l'alias "previous"."""
    import mlflow
    import numpy as np
    from mlflow import MlflowClient
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.linear_model import LinearRegression
    from sklearn.pipeline import make_pipeline

    from pipeline.data import prepare_features

    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(config.EXPERIMENT_NAME)
    client = MlflowClient()
    current = client.get_model_version_by_alias(config.MODEL_NAME, config.PRODUCTION_ALIAS).version

    rides = [{"PULocationID": 1, "DOLocationID": 2, "trip_distance": d} for d in (1.0, 2.0, 3.0)]
    model = make_pipeline(DictVectorizer(), LinearRegression())
    model.fit([prepare_features(r) for r in rides], [5.0, 8.0, 11.0])
    model[-1].coef_ = np.zeros(model[-1].coef_.shape[0] + 5)  # mauvaise dimension : predict() lèvera une erreur

    with mlflow.start_run(run_name="demo-modele-casse"):
        mlflow.set_tag("demo", "inject_failure")
        info = mlflow.sklearn.log_model(model, name="model", registered_model_name=config.MODEL_NAME)
    version = info.registered_model_version

    previous_alias = getattr(config, "PREVIOUS_ALIAS", "previous")
    client.set_registered_model_alias(config.MODEL_NAME, previous_alias, current)
    client.set_registered_model_alias(config.MODEL_NAME, config.PRODUCTION_ALIAS, version)
    requests.post(f"{config.API_URL}/reload", timeout=60)
    print(f"Version {version} (cassée) promue en production ; la version {current} garde l'alias "
          f"'{previous_alias}'.")


def mlflow_down() -> None:
    client = _docker()
    client.containers.get(config.MLFLOW_CONTAINER_NAME).stop()
    client.containers.get(config.API_CONTAINER_NAME).restart()
    print("MLflow arrêté et API redémarrée : elle ne peut plus charger son modèle.")


def recover() -> None:
    client = _docker()
    for name in (config.MLFLOW_CONTAINER_NAME, config.API_CONTAINER_NAME):
        container = client.containers.get(name)
        if container.status != "running":
            container.start()
            print(f"{name} relancé.")
    time.sleep(5)
    try:
        _set_fault("none")
    except Exception as exc:  # l'API peut être encore en train de démarrer
        print(f"Panne de l'API non réinitialisée ({exc}) : relancer `recover` dans quelques secondes.")


def traffic(per_second: float) -> None:
    """Trafic utilisateur réaliste : trajets aléatoires, statistiques toutes les 10 s."""
    ok = ko = fallback = 0
    last = time.time()
    print("Trafic simulé en cours (Ctrl+C pour arrêter)...")
    try:
        while True:
            ride = {"PULocationID": random.randint(1, 265), "DOLocationID": random.randint(1, 265),
                    "trip_distance": round(random.uniform(0.5, 15), 1)}
            try:
                resp = requests.post(f"{config.API_URL}/predict", json=ride, timeout=config.HTTP_TIMEOUT_SECONDS)
                if resp.status_code >= 500:
                    ko += 1
                else:
                    ok += 1
                    fallback += resp.json().get("degraded", False)
            except requests.RequestException:
                ko += 1
            if time.time() - last >= 10:
                print(f"{time.strftime('%H:%M:%S')}  OK={ok}  erreurs={ko}  dont secours={fallback}")
                ok = ko = fallback = 0
                last = time.time()
            time.sleep(1 / per_second)
    except KeyboardInterrupt:
        print("Trafic arrêté.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Banc de pannes pour l'agent Fiabilité.")
    parser.add_argument("mode", choices=["traffic", "crash", "errors", "latency", "bad-model",
                                         "mlflow-down", "recover"])
    parser.add_argument("--rate", type=float, default=0.3, help="part d'erreurs pour le mode errors")
    parser.add_argument("--seconds", type=float, default=2.0, help="latence ajoutée pour le mode latency")
    parser.add_argument("--rps", type=float, default=5.0, help="requêtes par seconde pour le mode traffic")
    args = parser.parse_args()

    actions = {
        "traffic": lambda: traffic(args.rps),
        "crash": crash,
        "errors": lambda: errors(args.rate),
        "latency": lambda: latency(args.seconds),
        "bad-model": bad_model,
        "mlflow-down": mlflow_down,
        "recover": recover,
    }
    actions[args.mode]()
    if args.mode in EXPECTED:
        print(f"Réaction attendue de l'agent : {EXPECTED[args.mode]}")


if __name__ == "__main__":
    main()
