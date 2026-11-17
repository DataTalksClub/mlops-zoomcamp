"""Entraîne le modèle taxi et l'enregistre dans le registre MLflow.

Usage :
    python -m pipeline.train --year 2023 --month 1
    python -m pipeline.train --year 2023 --month 1 --promote   # le met en production
Le tout premier modèle est mis en production automatiquement."""
from __future__ import annotations

import argparse
import time
import mlflow
import pandas as pd
import xgboost as xgb
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
from sklearn.pipeline import make_pipeline

from common import config
from pipeline.data import TARGET, read_dataframe, to_features

# Types XGBoost que MLflow peut recharger sans risque
XGBOOST_TYPES = ["xgboost.core.Booster", "xgboost.sklearn.XGBRegressor"]

PARAMS = {
    "learning_rate": 0.0959,
    "max_depth": 30,
    "min_child_weight": 1.06,
    "reg_alpha": 0.018,
    "reg_lambda": 0.0117,
    "n_estimators": 30,
    "objective": "reg:squarederror",
    "random_state": 42,
}


def next_month(year: int, month: int) -> tuple[int, int]:
    return (year, month + 1) if month < 12 else (year + 1, 1)


def has_production_model(client: MlflowClient) -> bool:
    try:
        client.get_model_version_by_alias(config.MODEL_NAME, config.PRODUCTION_ALIAS)
        return True
    except MlflowException:
        return False


def fit_and_register(df_train: pd.DataFrame, df_test: pd.DataFrame, tags: dict | None = None) -> dict:
    """Entraîne le pipeline, mesure le RMSE sur df_test et enregistre le modèle dans MLflow.

    Ne touche pas à l'alias production : c'est à l'appelant de décider.
    """
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(config.EXPERIMENT_NAME)
    pipeline = make_pipeline(DictVectorizer(), xgb.XGBRegressor(**PARAMS))

    with mlflow.start_run(tags=tags) as run:
        mlflow.log_params(PARAMS)
        start = time.perf_counter()
        pipeline.fit(to_features(df_train), df_train[TARGET].values)
        training_seconds = time.perf_counter() - start
        rmse = root_mean_squared_error(df_test[TARGET].values, pipeline.predict(to_features(df_test)))
        mlflow.log_metrics({"rmse": rmse, "training_seconds": training_seconds})
        info = mlflow.sklearn.log_model(
            pipeline,
            name="model",
            registered_model_name=config.MODEL_NAME,
            skops_trusted_types=XGBOOST_TYPES,
        )

    return {
        "run_id": run.info.run_id,
        "version": info.registered_model_version,
        "rmse": rmse,
        "training_seconds": training_seconds,
    }


def train(year: int, month: int, promote: bool = False) -> dict:
    df_train = read_dataframe(year, month)
    df_test = read_dataframe(*next_month(year, month))
    result = fit_and_register(df_train, df_test, tags={"train_period": f"{year}-{month:02d}"})

    client = MlflowClient()
    should_promote = promote or not has_production_model(client)
    if should_promote:
        client.set_registered_model_alias(config.MODEL_NAME, config.PRODUCTION_ALIAS, result["version"])

    result["promoted"] = should_promote
    print(result)
    return result
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entraîne le modèle de durée des trajets de taxi.")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--promote", action="store_true", help="mettre ce modèle en production")
    args = parser.parse_args()
    train(args.year, args.month, args.promote)