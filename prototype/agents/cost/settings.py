"""Paramètres de coûts du prototype (tarifs fictifs)."""
from __future__ import annotations

from dataclasses import dataclass, field

from common import config


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
        default_factory=lambda: config.COST_PER_CPU_SECOND
    )
    # remise d'un serveur "spot" (0.6 = 60 % moins cher)
    spot_discount: float = field(
        default_factory=lambda: config.COST_SPOT_DISCOUNT
    )
    monthly_budget: float = field(
        default_factory=lambda: config.MONTHLY_BUDGET
    )
    # estimation par défaut quand un modèle n'a encore aucun entraînement
    default_cpu_seconds_per_month_of_data: float = field(
        default_factory=lambda: config.DEFAULT_CPU_SECONDS_PER_MONTH_OF_DATA
    )
    # inactivité de l'API avant de suggérer un scale-to-zero (minutes)
    idle_minutes: float = field(default_factory=lambda: config.COST_IDLE_MINUTES)
    # marge de sécurité pour la recommandation de taille
    size_headroom: float = field(default_factory=lambda: config.COST_SIZE_HEADROOM)
    sizes: tuple[ServerSize, ...] = DEFAULT_SIZES
    hours_per_month: float = field(default_factory=lambda: config.COST_HOURS_PER_MONTH)
