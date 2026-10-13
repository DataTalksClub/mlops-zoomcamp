"""Mesure du temps CPU. Interface + faux pour les tests + Docker SDK."""
from __future__ import annotations

from typing import Dict, Protocol


class CpuCollector(Protocol):
    def cpu_seconds(self, container: str) -> float:
        """Temps CPU CUMULÉ du conteneur depuis son démarrage, en secondes."""
        ...


class FakeCollector:
    """Renvoie des valeurs fixées à la main (tests)."""

    def __init__(self, values: Dict[str, float] | None = None) -> None:
        self.values = dict(values or {})

    def cpu_seconds(self, container: str) -> float:
        return self.values.get(container, 0.0)


class DockerStatsCollector:
    """Lit les stats Docker (paquet `docker`). Import fait à l'usage."""

    def __init__(self, client=None) -> None:
        if client is None:
            import docker  # noqa: PLC0415
            client = docker.from_env()
        self._client = client

    def cpu_seconds(self, container: str) -> float:
        stats = self._client.containers.get(container).stats(stream=False)
        total_ns = stats["cpu_stats"]["cpu_usage"]["total_usage"]
        return total_ns / 1e9
