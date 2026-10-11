"""Point d'entrée de l'agent qualité.

Usage (depuis prototype/) :
    python -m agents.quality --year 2023 --month 2                        # cas normal
    python -m agents.quality --year 2023 --month 2 --scenario drift       # dérive fabriquée
    python -m agents.quality --year 2023 --month 2 --scenario corrupted   # données corrompues
    ajouter --dry-run pour ne rien publier (ni Redis, ni Postgres)
"""
from __future__ import annotations

import argparse

import mlflow
import pandas as pd

from agents.quality.checker import build_event, publish_quality_result
from agents.quality.drift import calculate_drift
from agents.quality.validation import validate_current_data
from common import config
from pipeline.data import DATA_DIR, read_dataframe


def load_raw(year: int, month: int) -> pd.DataFrame:
    """Parquet brut, non nettoyé (read_dataframe supprime les durées invalides)."""
    read_dataframe(year, month)  # garantit que le fichier est téléchargé
    return pd.read_parquet(DATA_DIR / f"green_tripdata_{year}-{month:02d}.parquet")


def apply_scenario(scenario: str, raw: pd.DataFrame, clean: pd.DataFrame):
    """Fabrique des données anormales pour la démonstration."""
    raw, clean = raw.copy(), clean.copy()
    if scenario == "drift":
        raw["trip_distance"] *= 1.5
        clean["trip_distance"] *= 1.5
    elif scenario == "corrupted":
        n = int(len(raw) * 0.10)  # 10 % de lignes corrompues
        raw.loc[raw.index[:n], "lpep_dropoff_datetime"] = (
            raw.loc[raw.index[:n], "lpep_pickup_datetime"] - pd.Timedelta(minutes=30)
        )
    return raw, clean


def run_check(model, reference, clean, raw):
    validation = validate_current_data(raw)
    drift = calculate_drift(reference, clean, model)
    return build_event(validation, drift["drift_score"], drift["num_drifted_columns"],
                       prediction_drift=drift["prediction_drift"])


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description="Agent qualité : validation + dérive.")
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--month", type=int, required=True)
    p.add_argument("--ref-year", type=int, default=2023)
    p.add_argument("--ref-month", type=int, default=1)
    p.add_argument("--scenario", choices=["normal", "drift", "corrupted"], default="normal")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    model = mlflow.sklearn.load_model(f"models:/{config.MODEL_NAME}@{config.PRODUCTION_ALIAS}")

    reference = read_dataframe(args.ref_year, args.ref_month)
    clean = read_dataframe(args.year, args.month)
    raw = load_raw(args.year, args.month)
    raw, clean = apply_scenario(args.scenario, raw, clean)

    event = run_check(model, reference, clean, raw)

    if args.dry_run:
        print(event.model_dump_json(indent=2))
        return

    from common.action_log import ActionLog
    from common.events import EventBus
    publish_quality_result(event, EventBus(), ActionLog())
    print(f"Publié : {event.type.value} ({event.severity.value}) reason={event.payload.get('reason')}")


if __name__ == "__main__":
    main()