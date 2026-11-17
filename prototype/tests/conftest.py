import numpy as np
import pandas as pd
import pytest

from common import config


def synthetic_month(year: int, month: int, n: int = 500) -> pd.DataFrame:
    """Petites données synthétiques au format NYC taxi, pour tester sans téléchargement."""
    rng = np.random.default_rng(year * 100 + month)
    df = pd.DataFrame({
        "PULocationID": rng.integers(1, 30, n).astype(str),
        "DOLocationID": rng.integers(1, 30, n).astype(str),
        "trip_distance": rng.uniform(0.5, 10, n),
    })
    df["duration"] = 4 + 3 * df.trip_distance + rng.normal(0, 1.5, n)
    return df


@pytest.fixture
def local_mlflow(tmp_path, monkeypatch):
    """MLflow local (SQLite) et données synthétiques à la place du téléchargement."""
    uri = f"sqlite:///{tmp_path / 'mlflow.db'}"
    monkeypatch.setattr(config, "MLFLOW_TRACKING_URI", uri)
    monkeypatch.setattr("pipeline.train.read_dataframe", synthetic_month)
    return uri