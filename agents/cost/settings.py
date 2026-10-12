"""Paramètres de l'agent Coûts (tarifs FICTIFS).

À terme, déplace ces valeurs dans prototype/common/config.py (la fiche
l'exige) et importe-les d'ici. Chaque valeur peut être surchargée par une
variable d'environnement, par exemple COST_MONTHLY_BUDGET=50.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    return float(raw) if raw not in (None, "") else default


@dataclass(frozen=True)
class ServerSize:
    name: str
    vcpus: float
    hourly_price: float  # tarif fictif, en "euros" fictifs par heure


DEFAULT_SIZES: tuple[ServerSize, ...] = (
    ServerSize("S", 1, 0.05),
    ServerSize("M", 2, 0.10),
    ServerSize("L", 4, 0.20),
)


@dataclass(frozen=True)
class CostConfig:
    # coût d'une seconde de CPU sur un serveur "standard"
    cost_per_cpu_second: float = field(
        default_factory=lambda: _env_float("COST_PER_CPU_SECOND", 0.0005)
    )
    # remise d'un serveur "spot" (0.6 = 60 % moins cher)
    spot_discount: float = field(
        default_factory=lambda: _env_float("COST_SPOT_DISCOUNT", 0.6)
    )
    monthly_budget: float = field(
        default_factory=lambda: _env_float("COST_MONTHLY_BUDGET", 50.0)
    )
    # estimation par défaut quand un modèle n'a encore aucun entraînement
    default_cpu_seconds_per_month_of_data: float = 600.0
    # inactivité de l'API avant de suggérer un scale-to-zero (minutes)
    idle_minutes: float = 30.0
    # marge de sécurité pour la recommandation de taille
    size_headroom: float = 0.30
    sizes: tuple[ServerSize, ...] = DEFAULT_SIZES
    hours_per_month: float = 730.0
