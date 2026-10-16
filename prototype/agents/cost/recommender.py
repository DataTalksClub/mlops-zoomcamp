"""Recommandations (calcul seulement). Aucune action sur l'infrastructure."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Sequence

from .settings import CostConfig, ServerSize


def _by_name(sizes: Sequence[ServerSize], name: str) -> ServerSize:
    for s in sizes:
        if s.name == name:
            return s
    raise ValueError(f"taille inconnue : {name}")


def recommend_size(used_vcpus: float, current_size: str, config: CostConfig) -> dict:
    """Propose la plus petite taille qui couvre `used_vcpus` + marge.

    `used_vcpus` : CPU réellement utilisé (pic ou percentile 95), en vCPU.
    """
    if used_vcpus < 0:
        raise ValueError("used_vcpus ne peut pas être négatif")
    sizes = sorted(config.sizes, key=lambda s: s.vcpus)
    current = _by_name(sizes, current_size)
    needed = used_vcpus * (1.0 + config.size_headroom)

    target = sizes[-1]  # à défaut, la plus grande
    for s in sizes:
        if s.vcpus >= needed:
            target = s
            break

    if target.vcpus < current.vcpus:
        action = "downsize"
    elif target.vcpus > current.vcpus:
        action = "upsize"
    else:
        action = "keep"

    monthly_saving = (current.hourly_price - target.hourly_price) * config.hours_per_month
    return {
        "action": action,
        "current": current.name,
        "recommended": target.name,
        "needed_vcpus": round(needed, 3),
        "monthly_saving": round(monthly_saving, 4),  # négatif si upsize
    }


def is_idle(last_request_at: Optional[datetime], now: datetime, config: CostConfig) -> bool:
    """Vrai si l'API n'a reçu aucune requête depuis `idle_minutes`."""
    if last_request_at is None:
        return True
    return (now - last_request_at) >= timedelta(minutes=config.idle_minutes)


def scale_to_zero_saving(idle_hours: float, size: str, config: CostConfig) -> dict:
    """Économie estimée si le serveur était arrêté pendant `idle_hours`."""
    if idle_hours < 0:
        raise ValueError("idle_hours ne peut pas être négatif")
    server = _by_name(config.sizes, size)
    return {
        "action": "scale_to_zero",
        "size": server.name,
        "idle_hours": idle_hours,
        "estimated_saving": round(idle_hours * server.hourly_price, 4),
    }
