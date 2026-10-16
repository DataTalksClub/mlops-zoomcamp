from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from common import config

REQUIRED_COLUMNS = {
    "lpep_pickup_datetime", "lpep_dropoff_datetime",
    "trip_distance", "PULocationID", "DOLocationID",
}


@dataclass
class ValidationResult:
    row_count: int = 0
    invalid_rows: int = 0
    invalid_share: float = 0.0
    share_missing_values: float = 0.0
    reasons: list[str] = field(default_factory=list)
    missing_columns: list[str] = field(default_factory=list)

    @property
    def is_critical(self) -> bool:
        return bool(self.missing_columns) or self.invalid_share >= config.CRITICAL_INVALID_SHARE


def validate_current_data(df: pd.DataFrame) -> ValidationResult:
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        return ValidationResult(row_count=len(df), reasons=["missing_required_columns"],
                                missing_columns=missing)

    duration = (df["lpep_dropoff_datetime"] - df["lpep_pickup_datetime"]).dt.total_seconds() / 60
    bad_duration = (duration < 0) | (duration > config.MAX_TRIP_MINUTES)
    bad_distance = (df["trip_distance"] < 0) | (df["trip_distance"] > config.MAX_TRIP_DISTANCE)
    bad_passengers = pd.Series(False, index=df.index)
    if "passenger_count" in df.columns:
        p = df["passenger_count"]
        bad_passengers = p.notna() & ((p <= 0) | (p > config.MAX_PASSENGERS))

    bad_any = bad_duration | bad_distance | bad_passengers
    reasons = [name for name, mask in [
        ("invalid_duration", bad_duration),
        ("invalid_distance", bad_distance),
        ("invalid_passenger_count", bad_passengers),
    ] if mask.any()]

    n = len(df)
    return ValidationResult(
        row_count=n,
        invalid_rows=int(bad_any.sum()),
        invalid_share=float(bad_any.sum() / n) if n else 0.0,
        share_missing_values=float(df[list(REQUIRED_COLUMNS)].isna().mean().mean()) if n else 0.0,
        reasons=reasons,
    )