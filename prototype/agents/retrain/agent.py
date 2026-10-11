"""Agent Retrain : entraîne un challenger, le compare à la production, puis le promeut ou le bloque.

Écoute : retrain_requested  (payload : period, requested_by, approved_by)
Publie : model_registered, puis model_promoted ou promotion_blocked
         (incident_opened si l'entraînement échoue)
Les versions ne sont jamais supprimées : l'ancienne production garde l'alias
"previous" pour permettre un rollback.
"""
from __future__ import annotations

from typing import Any, Callable

import mlflow
import pandas as pd
import requests
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException
from sklearn.metrics import root_mean_squared_error

from common import config
from common.action_log import ActionLog
from common.events import Event, EventBus, EventType, Severity
from pipeline import train as training
from pipeline.data import TARGET, read_dataframe, to_features

AGENT = "agent_retrain"


def parse_period(period: str | dict) -> list[tuple[int, int]]:
    """"2023-02" ou {"start": "2023-01", "end": "2023-03"} -> [(2023, 1), (2023, 2), (2023, 3)]."""
    if isinstance(period, str):
        start = end = period
    else:
        start, end = period["start"], period.get("end") or period["start"]
    year, month = map(int, start.split("-"))
    end_year, end_month = map(int, end.split("-"))
    if (year, month) > (end_year, end_month):
        raise ValueError(f"période invalide : {start} est après {end}")
    months = [(year, month)]
    while months[-1] != (end_year, end_month):
        months.append(training.next_month(*months[-1]))
    return months


def reload_api() -> bool:
    """Demande à l'API de charger le nouveau modèle en production."""
    try:
        return requests.post(f"{config.API_URL}/reload", timeout=30).ok
    except requests.RequestException:
        return False


class RetrainAgent:
    def __init__(
        self,
        bus: EventBus | None = None,
        log: ActionLog | None = None,
        read_data: Callable[[int, int], pd.DataFrame] = read_dataframe,
        reload: Callable[[], bool] = reload_api,
    ):
        self.bus = bus or EventBus()
        self.log = log or ActionLog()
        self.read_data = read_data
        self.reload = reload

    def run(self) -> None:
        print("Agent Retrain : en écoute de retrain_requested…")
        self.bus.listen(self.handle, types=[EventType.RETRAIN_REQUESTED])

    def handle(self, event: Event) -> dict[str, Any]:
        who = {
            "requested_by": event.payload.get("requested_by", event.source),
            "approved_by": event.payload.get("approved_by"),
        }
        try:
            months = parse_period(event.payload["period"])
            period = [f"{y}-{m:02d}" for y, m in months]
            self.log.record(AGENT, "retrain_started", event.model, {**who, "period": period})

            df_train = pd.concat([self.read_data(y, m) for y, m in months], ignore_index=True)
            df_test = self.read_data(*training.next_month(*months[-1]))
            challenger = training.fit_and_register(
                df_train, df_test, tags={"role": "challenger", "train_period": f"{period[0]}..{period[-1]}"}
            )
        except Exception as exc:  # l'agent doit continuer à écouter même si un entraînement échoue
            self.log.record(AGENT, "retrain_failed", event.model, {**who, "error": str(exc)})
            self.publish(EventType.INCIDENT_OPENED, Severity.CRITICAL, {**who, "error": str(exc)})
            return {"decision": "failed", "error": str(exc)}

        registered = {
            "version": challenger["version"],
            "rmse": challenger["rmse"],
            "training_seconds": challenger["training_seconds"],
            "period": period,
            **who,
        }
        self.log.record(AGENT, "challenger_registered", event.model, registered)
        self.publish(EventType.MODEL_REGISTERED, Severity.INFO, registered)

        return self.compare_and_decide(challenger, df_test, who)

    def compare_and_decide(self, challenger: dict, df_test: pd.DataFrame, who: dict) -> dict[str, Any]:
        client = MlflowClient(config.MLFLOW_TRACKING_URI)
        production = self.production_version(client)

        result = {
            "challenger_version": challenger["version"],
            "challenger_rmse": challenger["rmse"],
            "production_version": production,
            "production_rmse": None,
            "improvement": None,
            "min_improvement": config.MIN_IMPROVEMENT,
            **who,
        }
        if production is not None:
            # Même jeu de test pour les deux modèles
            model = mlflow.sklearn.load_model(f"models:/{config.MODEL_NAME}/{production}")
            production_rmse = root_mean_squared_error(df_test[TARGET].values, model.predict(to_features(df_test)))
            result["production_rmse"] = production_rmse
            result["improvement"] = (production_rmse - challenger["rmse"]) / production_rmse

        better = production is None or result["improvement"] > config.MIN_IMPROVEMENT
        if better:
            if production is not None:
                client.set_registered_model_alias(config.MODEL_NAME, config.PREVIOUS_ALIAS, production)
            client.set_registered_model_alias(config.MODEL_NAME, config.PRODUCTION_ALIAS, challenger["version"])
            client.set_model_version_tag(config.MODEL_NAME, challenger["version"], "decision", "promoted")
            result["api_reloaded"] = self.reload()
            self.log.record(AGENT, "model_promoted", config.MODEL_NAME, result)
            self.publish(EventType.MODEL_PROMOTED, Severity.INFO, result)
            return {"decision": "promoted", **result}

        client.set_model_version_tag(config.MODEL_NAME, challenger["version"], "decision", "blocked")
        result["reason"] = f"le challenger ne réduit pas l'erreur d'au moins {config.MIN_IMPROVEMENT:.0%}"
        self.log.record(AGENT, "promotion_blocked", config.MODEL_NAME, result)
        self.publish(EventType.PROMOTION_BLOCKED, Severity.WARNING, result)
        return {"decision": "blocked", **result}

    @staticmethod
    def production_version(client: MlflowClient) -> str | None:
        try:
            return client.get_model_version_by_alias(config.MODEL_NAME, config.PRODUCTION_ALIAS).version
        except MlflowException:
            return None

    def publish(self, type_: EventType, severity: Severity, payload: dict) -> None:
        event = Event(type=type_, source=AGENT, severity=severity, payload=payload)
        self.bus.publish(event)
        print(f"[{severity.value}] {type_.value} {payload}")