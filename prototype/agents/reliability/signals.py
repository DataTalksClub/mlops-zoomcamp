"""Collecte des signaux externes à l'API pour le diagnostic : état du conteneur,
boucle de crash, ressources, dépendances (MLflow, Redis, Postgres) et âge du
modèle servi. Chaque sonde est isolée : une sonde en échec donne un signal
"KO", jamais une exception."""
from __future__ import annotations

import time
from collections import deque
from typing import Callable

import requests

from agents.reliability.diagnosis import Signals
from agents.reliability.metrics import WindowStats
from common import config

CRASH_LOOP_WINDOW_SECONDS = 600  # fenêtre de comptage des redémarrages (10 min)


def memory_percent(stats: dict) -> float | None:
    """Mémoire utilisée en % de la limite du conteneur (cache disque exclu, comme `docker stats`)."""
    mem = stats.get("memory_stats") or {}
    usage, limit = mem.get("usage"), mem.get("limit")
    if not usage or not limit:
        return None
    cache = (mem.get("stats") or {}).get("inactive_file", 0)
    return round((usage - cache) / limit * 100, 1)


def cpu_percent(stats: dict) -> float | None:
    """CPU en %, calculé entre deux mesures Docker (cpu_stats et precpu_stats)."""
    cpu, pre = stats.get("cpu_stats") or {}, stats.get("precpu_stats") or {}
    try:
        cpu_delta = cpu["cpu_usage"]["total_usage"] - pre["cpu_usage"]["total_usage"]
        system_delta = cpu["system_cpu_usage"] - pre["system_cpu_usage"]
    except (KeyError, TypeError):
        return None
    if system_delta <= 0:
        return None
    cpus = cpu.get("online_cpus") or 1
    return round(cpu_delta / system_delta * cpus * 100, 1)


class ModelAgeTracker:
    """Mesure depuis quand la version servie a changé, en l'observant cycle après cycle.

    Au premier passage, l'âge est inconnu (None) : sans preuve, on ne soupçonne
    pas le modèle. L'agent n'a donc pas besoin que Retrain enregistre une date
    de promotion."""

    def __init__(self):
        self.version: int | None = None
        self.since: float | None = None
        self._trust_next_change = False

    def trust_next_change(self) -> None:
        """Le prochain changement de version vient de l'agent lui-même (rollback) : la
        version restaurée est connue, elle ne doit pas être soupçonnée comme une promotion."""
        self._trust_next_change = True

    def update(self, version: int, now: float) -> float | None:
        if version and version != self.version:   # version 0 = aucun modèle chargé : ignorée
            first_observation = self.version is None
            self.version = version
            self.since = None if (first_observation or self._trust_next_change) else now
            self._trust_next_change = False
        return None if self.since is None else now - self.since


class SignalCollector:
    def __init__(self, docker_client=None, http=None, redis_client=None,
                 postgres_check: Callable[[], None] | None = None):
        self._docker = docker_client
        self.http = http or requests
        self._redis = redis_client
        self._postgres_check = postgres_check
        self._restart_history: deque[tuple[float, int]] = deque()
        self.model_age = ModelAgeTracker()

    def trust_next_model_change(self) -> None:
        self.model_age.trust_next_change()

    def observe(self, window: WindowStats, now: float) -> None:
        """Observation légère à CHAQUE cycle (même sans incident) : sans elle, l'agent ne
        verrait pas une promotion survenue juste avant une panne et ne pourrait pas
        soupçonner le nouveau modèle."""
        if window.reachable:
            self.model_age.update(window.model_version, now)

    def collect(self, window: WindowStats, now: float | None = None) -> Signals:
        now = time.time() if now is None else now
        status, restarts, mem, cpu = self._container(now)
        age = self.model_age.update(window.model_version, now) if window.reachable else None
        return Signals(
            container_status=status,
            restarts_recent=restarts,
            memory_percent=mem,
            cpu_percent=cpu,
            mlflow_ok=self._mlflow_ok(),
            redis_ok=self._redis_ok(),
            postgres_ok=self._postgres_ok(),
            model_age_seconds=age,
        )

    # --- Conteneur de l'API ---
    @property
    def docker(self):
        if self._docker is None:
            import docker
            self._docker = docker.from_env()
        return self._docker

    def _container(self, now: float) -> tuple[str, int, float | None, float | None]:
        try:
            container = self.docker.containers.get(config.API_CONTAINER_NAME)
        except Exception:
            return "unknown", 0, None, None  # Docker injoignable ou conteneur supprimé

        # RestartCount est cumulé par Docker : on compare à la valeur d'il y a 10 min.
        count = int(container.attrs.get("RestartCount", 0))
        self._restart_history.append((now, count))
        while now - self._restart_history[0][0] > CRASH_LOOP_WINDOW_SECONDS:
            self._restart_history.popleft()
        restarts = count - self._restart_history[0][1]

        mem = cpu = None
        if container.status == "running":
            try:
                stats = container.stats(stream=False)
                mem, cpu = memory_percent(stats), cpu_percent(stats)
            except Exception:
                pass
        return container.status, restarts, mem, cpu

    # --- Dépendances ---
    def _mlflow_ok(self) -> bool:
        try:
            resp = self.http.get(f"{config.MLFLOW_TRACKING_URI}/health", timeout=config.HTTP_TIMEOUT_SECONDS)
            return resp.status_code == 200
        except Exception:
            return False

    def _redis_ok(self) -> bool:
        try:
            if self._redis is None:
                import redis
                self._redis = redis.Redis.from_url(config.REDIS_URL, socket_timeout=config.HTTP_TIMEOUT_SECONDS)
            return bool(self._redis.ping())
        except Exception:
            return False

    def _postgres_ok(self) -> bool:
        try:
            (self._postgres_check or self._default_postgres_check)()
            return True
        except Exception:
            return False

    def _default_postgres_check(self) -> None:
        from sqlalchemy import create_engine, text
        if not hasattr(self, "_engine"):
            self._engine = create_engine(config.DATABASE_URL, pool_pre_ping=True,
                                         connect_args={"connect_timeout": int(config.HTTP_TIMEOUT_SECONDS)})
        with self._engine.connect() as conn:
            conn.execute(text("SELECT 1"))