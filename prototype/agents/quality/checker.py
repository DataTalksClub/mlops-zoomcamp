from __future__ import annotations

from common import config
from common.events import Event, EventType, Severity

SOURCE = "agent_qualite"


def build_event(validation, drift_score: float, num_drifted_columns: int,
                prediction_drift: float = 0.0) -> Event:
    payload = {
        "drift_score": float(drift_score),
        "drift_threshold": config.DRIFT_THRESHOLD,
        "prediction_drift": float(prediction_drift),
        "column_drift_threshold": config.COLUMN_DRIFT_THRESHOLD,
        "num_drifted_columns": int(num_drifted_columns),
        "share_missing_values": validation.share_missing_values,
        "row_count": validation.row_count,
        "invalid_rows": validation.invalid_rows,
        "invalid_share": validation.invalid_share,
        "invalid_reasons": validation.reasons,
    }
    drifted = (drift_score >= config.DRIFT_THRESHOLD
               or prediction_drift >= config.COLUMN_DRIFT_THRESHOLD)
    if validation.is_critical:
        payload["reason"] = "corrupted_input_data"
        return Event(type=EventType.DRIFT_DETECTED, source=SOURCE,
                     severity=Severity.CRITICAL, payload=payload)
    if drifted:
        payload["reason"] = "distribution_drift"
        return Event(type=EventType.DRIFT_DETECTED, source=SOURCE,
                     severity=Severity.WARNING, payload=payload)
    return Event(type=EventType.QUALITY_OK, source=SOURCE,
                 severity=Severity.INFO, payload=payload)


def publish_quality_result(event: Event, event_bus, action_log) -> None:
    """Journalise puis publie."""
    action_log.record(agent=SOURCE, action=event.type.value,
                      model=event.model, details=event.payload)
    event_bus.publish(event)