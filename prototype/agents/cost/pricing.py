"""Tarifs fictifs : serveur standard et serveur spot."""
from __future__ import annotations

from typing import Dict

from .calculator import cost
from .settings import CostConfig


def spot_rate(config: CostConfig) -> float:
    return config.cost_per_cpu_second * (1.0 - config.spot_discount)


def price_options(cpu_seconds: float, config: CostConfig) -> Dict[str, dict]:
    """Coût d'un même job sur serveur standard et sur serveur spot."""
    standard = cost(cpu_seconds, config.cost_per_cpu_second)
    spot = cost(cpu_seconds, spot_rate(config))
    return {
        "standard": {"cost": round(standard, 6)},
        "spot": {"cost": round(spot, 6), "saving": round(standard - spot, 6)},
    }
