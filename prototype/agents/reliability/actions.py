"""Actions de remédiation de l'agent Fiabilité, snapshot et restauration.

Chaque action renvoie un ActionResult et ne lève jamais d'exception : un
échec est une information pour l'agent, qui passe à l'action suivante.
Docker, MLflow, HTTP et la commande système sont injectables : en test on
passe de faux objets, en production les vrais."""
from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import requests

from agents.reliability.catalog import Action
from common import config

# L'alias "previous" est posé par l'agent Retrain lors d'une promotion.
PREVIOUS_ALIAS = getattr(config, "PREVIOUS_ALIAS", "previous")
COMPOSE_FILE = Path(__file__).resolve().parents[2] / "docker-compose.yml"


@dataclass(frozen=True)
class ActionResult:
    action: str
    success: bool
    detail: str
    duration_seconds: float = 0.0


@dataclass(frozen=True)
class SystemSnapshot:
    """État capturé avant une remédiation pilotée par le LLM."""
    taken_at: float
    production_version: str | None
    containers_running: dict[str, bool]
    complete: bool  # False si MLflow ou Docker étaient injoignables : retour arrière non garanti


class ReliabilityActions:
    def __init__(self, docker_client=None, mlflow_client=None, http=None,
                 runner: Callable[[list[str]], None] | None = None):
        self._docker = docker_client
        self._mlflow = mlflow_client
        self.http = http or requests
        self.runner = runner or self._run_command

    # --- Clients créés à la demande (les tests n'ont besoin ni de Docker ni de MLflow) ---
    @property
    def docker(self):
        if self._docker is None:
            import docker
            self._docker = docker.from_env()
        return self._docker

    @property
    def mlflow(self):
        if self._mlflow is None:
            from mlflow import MlflowClient
            self._mlflow = MlflowClient(tracking_uri=config.MLFLOW_TRACKING_URI)
        return self._mlflow

    # --- Point d'entrée ---
    def execute(self, action: Action) -> ActionResult:
        handlers = {
            Action.RESTART_API: lambda: self._restart(config.API_CONTAINER_NAME),
            Action.RECREATE_API: self._recreate_api,
            Action.RELOAD_MODEL: self._reload_model,
            Action.ROLLBACK_MODEL: self._rollback_model,
            Action.DEGRADED_MODE: lambda: self._set_degraded(True),
            Action.RESTART_REDIS: lambda: self._restart(config.REDIS_CONTAINER_NAME),
            Action.RESTART_MLFLOW: lambda: self._restart(config.MLFLOW_CONTAINER_NAME),
        }
        handler = handlers.get(action)
        if handler is None:  # ESCALATE : c'est l'agent qui publie l'événement, pas une action système
            return ActionResult(action.value, False, "action non exécutable ici (gérée par l'agent)")
        return self._run(action.value, handler)

    def restart_container(self, name: str) -> ActionResult:
        return self._run(f"restart:{name}", lambda: self._restart(name))

    def exit_degraded_mode(self) -> ActionResult:
        return self._run("exit_degraded_mode", lambda: self._set_degraded(False))

    # --- Snapshot / restauration ---
    def production_version(self) -> str | None:
        try:
            return str(self.mlflow.get_model_version_by_alias(config.MODEL_NAME, config.PRODUCTION_ALIAS).version)
        except Exception:
            return None

    def take_snapshot(self) -> SystemSnapshot:
        running, docker_ok = {}, True
        for name in config.ALLOWED_CONTAINERS:
            try:
                running[name] = self.docker.containers.get(name).status == "running"
            except Exception:
                running[name], docker_ok = False, False
        version = self.production_version()
        return SystemSnapshot(time.time(), version, running, complete=docker_ok and version is not None)

    def restore(self, snap: SystemSnapshot) -> ActionResult:
        """Remet le système dans l'état du snapshot. Le mode dégradé n'est pas
        touché : après des tentatives ratées, le service doit rester en ligne."""
        def _restore() -> str:
            steps = []
            if snap.production_version and self.production_version() != snap.production_version:
                self.mlflow.set_registered_model_alias(config.MODEL_NAME, config.PRODUCTION_ALIAS,
                                                       snap.production_version)
                self._reload_model()
                steps.append(f"alias production remis sur la version {snap.production_version}")
            for name, was_running in snap.containers_running.items():
                container = self.docker.containers.get(name)
                if was_running and container.status != "running":
                    container.start()
                    steps.append(f"{name} relancé")
            return "; ".join(steps) or "rien à restaurer"
        return self._run("restore_snapshot", _restore)

    # --- Implémentations ---
    def _run(self, name: str, fn: Callable[[], str]) -> ActionResult:
        start = time.perf_counter()
        try:
            return ActionResult(name, True, fn(), time.perf_counter() - start)
        except Exception as exc:
            return ActionResult(name, False, f"{type(exc).__name__}: {exc}", time.perf_counter() - start)

    def _restart(self, name: str) -> str:
        if name not in config.ALLOWED_CONTAINERS:
            raise PermissionError(f"conteneur '{name}' hors de la liste autorisée")
        self.docker.containers.get(name).restart(timeout=10)
        return f"conteneur {name} redémarré"

    def _recreate_api(self) -> str:
        self.runner(["docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d",
                     "--force-recreate", "--no-deps", config.API_SERVICE_NAME])
        return "conteneur de l'API recréé"

    @staticmethod
    def _run_command(cmd: list[str]) -> None:
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)

    def _reload_model(self) -> str:
        resp = self.http.post(f"{config.API_URL}/reload", timeout=config.ACTION_HTTP_TIMEOUT_SECONDS)
        resp.raise_for_status()
        return f"modèle rechargé : {resp.json()}"

    def find_rollback_target(self, current: str | None) -> str | None:
        """Dernière version saine (tag healthy=true), sinon l'alias previous.
        Jamais la version actuelle ni une version déjà marquée rolled_back."""
        def usable(v) -> bool:
            return str(v.version) != current and v.tags.get("rolled_back") != "true"

        versions = self.mlflow.search_model_versions(f"name='{config.MODEL_NAME}'")
        healthy = [v for v in versions if usable(v) and v.tags.get("healthy") == "true"]
        if healthy:
            return str(max(healthy, key=lambda v: int(v.version)).version)
        try:
            previous = self.mlflow.get_model_version_by_alias(config.MODEL_NAME, PREVIOUS_ALIAS)
        except Exception:
            return None
        return str(previous.version) if usable(previous) else None

    def _rollback_model(self) -> str:
        current = self.production_version()
        target = self.find_rollback_target(current)
        if target is None:
            raise RuntimeError("aucune version saine disponible pour un rollback")
        self.mlflow.set_registered_model_alias(config.MODEL_NAME, config.PRODUCTION_ALIAS, target)
        if current is not None:  # l'agent Retrain ne doit plus jamais repromouvoir cette version
            self.mlflow.set_model_version_tag(config.MODEL_NAME, current, "rolled_back", "true")
        self._reload_model()
        return f"rollback de la version {current} vers la version {target}"

    def _set_degraded(self, enabled: bool) -> str:
        resp = self.http.post(f"{config.API_URL}/degraded", json={"enabled": enabled},
                              timeout=config.HTTP_TIMEOUT_SECONDS)
        resp.raise_for_status()
        return "mode dégradé activé" if enabled else "mode dégradé désactivé"