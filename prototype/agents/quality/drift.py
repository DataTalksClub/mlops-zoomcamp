from __future__ import annotations

import pandas as pd
from evidently import DataDefinition, Dataset, Report
from evidently.metrics import ValueDrift

from common import config
from pipeline.data import to_features

NUMERIC = ["trip_distance", "prediction"]
CATEGORICAL = ["PU", "DO"]


def build_frame(df: pd.DataFrame, model) -> pd.DataFrame:
    """Mêmes variables que l'entraînement + prédiction du modèle."""
    feats = to_features(df)
    frame = pd.DataFrame({
        "trip_distance": [f["trip_distance"] for f in feats],
        "PU": df["PULocationID"].astype(str).values,
        "DO": df["DOLocationID"].astype(str).values,
    })
    frame["prediction"] = model.predict(feats)
    return frame


def calculate_drift(reference: pd.DataFrame, current: pd.DataFrame, model) -> dict:
    ref = build_frame(reference, model)
    cur = build_frame(current, model)
    schema = DataDefinition(numerical_columns=NUMERIC, categorical_columns=CATEGORICAL)
    thr = config.COLUMN_DRIFT_THRESHOLD

    metrics = [ValueDrift(column=c, method="wasserstein", threshold=thr) for c in NUMERIC]
    metrics += [ValueDrift(column=c, method="jensenshannon", threshold=thr) for c in CATEGORICAL]
    columns = NUMERIC + CATEGORICAL

    snapshot = Report(metrics).run(
        Dataset.from_pandas(cur, data_definition=schema),
        Dataset.from_pandas(ref, data_definition=schema),
    )
    scores = {c: float(m["value"]) for c, m in zip(columns, snapshot.dict()["metrics"])}
    drifted = [c for c, v in scores.items() if v >= thr]
    return {
        "drift_score": len(drifted) / len(columns),
        "num_drifted_columns": len(drifted),
        "prediction_drift": scores["prediction"],
        "column_scores": scores,
    }