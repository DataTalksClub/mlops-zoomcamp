"""Sondes synthétiques : à chaque cycle, l'agent envoie lui-même quelques
prédictions avec l'en-tête X-Bypass-Degraded. Il mesure ainsi le vrai modèle
même sans trafic utilisateur, et même quand l'API est en mode dégradé."""
from __future__ import annotations

import math
import time
from dataclasses import dataclass

import requests

from common import config

PROBE_PAYLOAD = {"PULocationID": 43, "DOLocationID": 151, "trip_distance": 1.8}
BYPASS_HEADERS = {"X-Bypass-Degraded": "1"}


@dataclass(frozen=True)
class ProbeResult:
    sent: int
    failed: int
    p95_latency: float | None

    @property
    def failure_rate(self) -> float:
        return self.failed / self.sent if self.sent else 0.0

    @property
    def ok(self) -> bool:
        if self.sent == 0:  # sondes désactivées : pas d'information, on ne conclut rien
            return True
        slow = self.p95_latency is not None and self.p95_latency > config.MAX_LATENCY_SECONDS
        return self.failure_rate <= config.MAX_ERROR_RATE and not slow


def percentile(values: list[float], q: float) -> float | None:
    """Percentile par rang le plus proche (suffisant pour une dizaine de mesures)."""
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)]


def run_probes(api_url: str | None = None, count: int | None = None, session=None) -> ProbeResult:
    api_url = api_url or config.API_URL
    count = config.PROBE_COUNT if count is None else count
    http = session or requests
    failed, latencies, unreachable_streak = 0, [], 0
    for i in range(count):
        start = time.perf_counter()
        try:
            resp = http.post(f"{api_url}/predict", json=PROBE_PAYLOAD, headers=BYPASS_HEADERS,
                             timeout=config.HTTP_TIMEOUT_SECONDS)
            unreachable_streak = 0
            if resp.status_code >= 500:
                failed += 1
        except Exception:  # timeout, connexion refusée : la sonde échoue
            failed += 1
            unreachable_streak += 1
        latencies.append(time.perf_counter() - start)
        if unreachable_streak >= config.PROBE_MAX_CONSECUTIVE_FAILURES:
            # API injoignable : inutile d'attendre les timeouts des sondes restantes,
            # le cycle de l'agent doit rester court (sinon les vérifications dérivent).
            failed += count - (i + 1)
            break
    return ProbeResult(sent=count, failed=failed, p95_latency=percentile(latencies, 0.95))
