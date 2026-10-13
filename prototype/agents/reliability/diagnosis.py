"""Diagnostic : cause probable d'un incident et chaîne d'actions à tenter.

Règles déterministes, évaluées dans un ordre de priorité : d'abord
l'infrastructure (conteneur), puis les dépendances, les ressources, le
modèle et enfin la charge. Si aucune règle ne correspond : UNKNOWN, avec la
chaîne la plus large."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agents.reliability.catalog import Action
from agents.reliability.metrics import WindowStats
from common import config


class Cause(str, Enum):
    CRASH_LOOP = "crash_loop"
    API_DOWN = "api_down"
    API_UNRESPONSIVE = "api_unresponsive"
    POSTGRES_DOWN = "postgres_down"
    MLFLOW_DOWN = "mlflow_down"
    REDIS_DOWN = "redis_down"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    MODEL_UNAVAILABLE = "model_unavailable"
    BAD_MODEL = "bad_model"
    OVERLOAD = "overload"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Signals:
    """Signaux externes à l'API, collectés par l'agent (Docker, MLflow, services)."""
    container_status: str = "running"         # running | exited | dead | restarting | unknown
    restarts_recent: int = 0                  # redémarrages du conteneur dans les 10 dernières minutes
    memory_percent: float | None = None
    cpu_percent: float | None = None
    mlflow_ok: bool = True
    redis_ok: bool = True
    postgres_ok: bool = True
    model_age_seconds: float | None = None    # temps depuis la promotion du modèle servi


@dataclass(frozen=True)
class Diagnosis:
    cause: Cause
    component: str                    # composant touché (sert au score de gravité)
    playbook: tuple[Action, ...]      # actions à tenter, dans l'ordre
    evidence: tuple[str, ...]         # faits qui justifient le diagnostic (rapport, LLM, juge)


def diagnose(window: WindowStats, signals: Signals) -> Diagnosis:
    significant = window.requests >= config.MIN_REQUESTS
    errors_high = significant and window.error_rate > config.MAX_ERROR_RATE
    slow = window.p95_latency is not None and window.p95_latency > config.MAX_LATENCY_SECONDS

    # 1. Infrastructure : le conteneur lui-même
    if signals.container_status == "restarting" or signals.restarts_recent >= config.CRASH_LOOP_RESTARTS:
        return Diagnosis(Cause.CRASH_LOOP, "api", (Action.RECREATE_API, Action.ESCALATE),
                         (f"conteneur en boucle de redémarrage ({signals.restarts_recent} en 10 min) : "
                          "un simple redémarrage ne suffira pas",))
    if signals.container_status in ("exited", "dead"):
        return Diagnosis(Cause.API_DOWN, "api", (Action.RESTART_API, Action.RECREATE_API, Action.ESCALATE),
                         (f"conteneur de l'API à l'état '{signals.container_status}'",))
    if not window.reachable:
        return Diagnosis(Cause.API_UNRESPONSIVE, "api",
                         (Action.RESTART_API, Action.RECREATE_API, Action.ESCALATE),
                         ("conteneur démarré mais l'API ne répond pas (processus bloqué ?)",))

    # 2. Dépendances
    if not signals.postgres_ok:
        return Diagnosis(Cause.POSTGRES_DOWN, "postgres", (Action.ESCALATE,),
                         ("Postgres injoignable : risque sur les données, intervention humaine uniquement",))
    if not signals.mlflow_ok:
        # Pas de redémarrage de l'API ni de rollback : sans MLflow, l'API ne pourrait plus
        # recharger de modèle et perdrait celui qu'elle a en mémoire.
        return Diagnosis(Cause.MLFLOW_DOWN, "mlflow", (Action.DEGRADED_MODE, Action.ESCALATE),
                         ("MLflow injoignable : ni redémarrage de l'API ni rollback possibles sans risque",))
    if not signals.redis_ok:
        return Diagnosis(Cause.REDIS_DOWN, "redis", (Action.RESTART_REDIS, Action.ESCALATE),
                         ("Redis injoignable : les agents ne peuvent plus communiquer",))

    # 3. Ressources
    mem, cpu = signals.memory_percent, signals.cpu_percent
    if (mem is not None and mem >= config.RESOURCE_MEMORY_PERCENT) or (
            cpu is not None and cpu >= config.RESOURCE_CPU_PERCENT):
        return Diagnosis(Cause.RESOURCE_EXHAUSTION, "api", (Action.RESTART_API, Action.ESCALATE),
                         (f"ressources saturées (mémoire {mem}%, CPU {cpu}%)",))

    # 4. Modèle
    if not window.model_loaded:
        return Diagnosis(Cause.MODEL_UNAVAILABLE, "api",
                         (Action.RELOAD_MODEL, Action.ROLLBACK_MODEL, Action.DEGRADED_MODE, Action.ESCALATE),
                         ("l'API tourne mais n'a aucun modèle chargé",))
    age = signals.model_age_seconds
    if errors_high and age is not None and age < config.BAD_MODEL_WINDOW_MINUTES * 60:
        return Diagnosis(Cause.BAD_MODEL, "api", (Action.ROLLBACK_MODEL, Action.DEGRADED_MODE, Action.ESCALATE),
                         (f"erreurs à {window.error_rate:.0%} apparues {age / 60:.0f} min après la "
                          f"promotion de la version {window.model_version}",))

    # 5. Charge
    if slow and not errors_high:
        return Diagnosis(Cause.OVERLOAD, "api", (Action.DEGRADED_MODE, Action.ESCALATE),
                         (f"latence p95 de {window.p95_latency:.2f} s sans erreurs : surcharge probable",))

    # 6. Rien ne correspond : chaîne la plus large
    return Diagnosis(Cause.UNKNOWN, "api",
                     (Action.RESTART_API, Action.ROLLBACK_MODEL, Action.DEGRADED_MODE, Action.ESCALATE),
                     (f"cause non identifiée (erreurs {window.error_rate:.0%}, p95 {window.p95_latency})",))