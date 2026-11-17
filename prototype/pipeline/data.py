"""Chargement des données NYC green taxi, avec un cache local dans prototype/data/."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet"

CATEGORICAL = ["PULocationID", "DOLocationID"]
NUMERICAL = ["trip_distance"]
TARGET = "duration"


def read_dataframe(year: int, month: int) -> pd.DataFrame:
    """Lit un mois de données (téléchargé une seule fois, puis lu depuis le disque)."""
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / f"green_tripdata_{year}-{month:02d}.parquet"
    if not path.exists():
        print(f"Téléchargement de {path.name}…")
        pd.read_parquet(URL.format(year=year, month=month)).to_parquet(path)
    df = pd.read_parquet(path)

    df[TARGET] = (df.lpep_dropoff_datetime - df.lpep_pickup_datetime).dt.total_seconds() / 60
    df = df[(df[TARGET] >= 1) & (df[TARGET] <= 60)].copy()
    df[CATEGORICAL] = df[CATEGORICAL].astype(str)
    return df


def to_features(df: pd.DataFrame) -> list[dict]:
    """Même transformation à l'entraînement et dans l'API."""
    records = df[CATEGORICAL + NUMERICAL].to_dict(orient="records")
    return [prepare_features(r) for r in records]


def prepare_features(ride: dict) -> dict:
    return {
        "PU_DO": f"{ride['PULocationID']}_{ride['DOLocationID']}",
        "trip_distance": float(ride["trip_distance"]),
    }