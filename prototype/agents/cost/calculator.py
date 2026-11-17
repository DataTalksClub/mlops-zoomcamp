"""Calculs de coût : fonctions pures, sans entrée/sortie."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional, Sequence, Tuple


def cost(cpu_seconds: float, rate_per_cpu_second: float) -> float:
    """Coût = temps CPU x tarif fictif."""
    if cpu_seconds < 0:
        raise ValueError("cpu_seconds ne peut pas être négatif")
    if rate_per_cpu_second < 0:
        raise ValueError("le tarif ne peut pas être négatif")
    return cpu_seconds * rate_per_cpu_second


def month_key(when: datetime) -> str:
    """Clé de mois, ex. '2026-10'."""
    return when.strftime("%Y-%m")


def would_exceed(month_total: float, estimate: float, budget: float) -> bool:
    """Vrai si (coût du mois + estimation) dépasse STRICTEMENT le budget.

    Pile au budget n'est pas un dépassement.
    """
    return (month_total + estimate) > budget


def estimate_cpu_seconds(
    history: Sequence[Tuple[float, int]],
    months: Optional[int],
    default_per_month: float,
) -> float:
    """Estime le CPU d'un futur entraînement.

    `history` : liste de (cpu_seconds, mois_de_données) des entraînements
    passés du modèle. On calcule le CPU moyen par mois de données, puis on
    le multiplie par la période demandée (1 mois si non précisée).
    Sans historique, on utilise `default_per_month`.
    """
    wanted = months if months and months > 0 else 1
    per_month = _mean_cpu_per_month(history)
    if per_month is None:
        per_month = default_per_month
    return per_month * wanted


def _mean_cpu_per_month(history: Iterable[Tuple[float, int]]) -> Optional[float]:
    rates = [cpu / m for cpu, m in history if m and m > 0]
    if not rates:
        return None
    return sum(rates) / len(rates)
