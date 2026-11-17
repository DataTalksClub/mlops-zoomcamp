"""Catalogue fermé des actions de l'agent Fiabilité.

Seules ces actions existent : le playbook, le LLM et le juge choisissent
dans cette liste, jamais en dehors. Le risque décide qui a le droit de les
lancer (en niveau moyen, le LLM n'a accès qu'aux actions à risque faible)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Action(str, Enum):
    RESTART_API = "restart_api"
    RECREATE_API = "recreate_api"
    RELOAD_MODEL = "reload_model"
    ROLLBACK_MODEL = "rollback_model"
    DEGRADED_MODE = "degraded_mode"
    RESTART_REDIS = "restart_redis"
    RESTART_MLFLOW = "restart_mlflow"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class ActionSpec:
    description: str  # texte lisible, réutilisé dans le prompt du LLM et du juge
    risk: str         # "low" ou "high"
    reversible: bool


CATALOG: dict[Action, ActionSpec] = {
    Action.RESTART_API: ActionSpec("Redémarrer le conteneur de l'API", "low", True),
    Action.RECREATE_API: ActionSpec("Recréer le conteneur de l'API à partir de son image", "low", True),
    Action.RELOAD_MODEL: ActionSpec("Recharger le modèle en production depuis MLflow (/reload)", "low", True),
    Action.ROLLBACK_MODEL: ActionSpec("Remettre en production la dernière version saine du modèle", "high", True),
    Action.DEGRADED_MODE: ActionSpec("Servir un modèle de secours simple en attendant la réparation", "low", True),
    Action.RESTART_REDIS: ActionSpec("Redémarrer Redis (bus d'événements)", "low", True),
    Action.RESTART_MLFLOW: ActionSpec("Redémarrer MLflow (registre des modèles)", "high", True),
    Action.ESCALATE: ActionSpec("Prévenir un humain avec le rapport d'incident", "low", True),
}

LOW_RISK_ACTIONS = frozenset(a for a, spec in CATALOG.items() if spec.risk == "low")