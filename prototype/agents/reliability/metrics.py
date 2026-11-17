"""Lecture des métriques de l'API et calcul des indicateurs sur une fenêtre.

L'API expose des compteurs cumulés (/metrics). L'agent en prend une photo
(Snapshot) à chaque cycle et compare deux photos successives pour obtenir
le trafic, le taux d'erreurs et la latence p95 de la fenêtre (WindowStats)."""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

import requests
from prometheus_client.parser import text_string_to_metric_families

from common import config


@dataclass(frozen=True)
class Snapshot:
    """Photo des compteurs de l'API à un instant donné."""
    timestamp: float
    reachable: bool                     # /metrics a répondu
    requests: float = 0.0               # requêtes cumulées sur la route surveillée
    errors: float = 0.0                 # dont réponses 5xx
    buckets: dict[float, float] = field(default_factory=dict)  # borne "le" -> nombre cumulé
    model_loaded: bool = False
    model_version: int = 0
    health_ok: bool = False             # /health a répondu 200
    error: str | None = None            # raison si l'API est injoignable


@dataclass(frozen=True)
class WindowStats:
    """Indicateurs calculés entre deux photos (une fenêtre de surveillance)."""
    duration: float                     # secondes entre les deux photos
    reachable: bool
    requests: float
    errors: float
    error_rate: float                   # 1.0 si l'API est injoignable (indisponibilité totale)
    p95_latency: float | None           # None si aucune requête dans la fenêtre
    model_loaded: bool
    model_version: int
    health_ok: bool
    counter_reset: bool                 # compteurs remis à zéro (redémarrage) : base = 0


def parse_metrics(text: str, endpoint: str | None = None) -> dict:
    """Extrait du texte Prometheus les valeurs utiles pour la route surveillée."""
    endpoint = endpoint or config.MONITORED_ENDPOINT
    values = {"requests": 0.0, "errors": 0.0, "buckets": {}, "model_loaded": False, "model_version": 0}
    for family in text_string_to_metric_families(text):
        for s in family.samples:
            if s.name == "api_requests_total" and s.labels.get("endpoint") == endpoint:
                values["requests"] += s.value
                if s.labels.get("status", "").startswith("5"):
                    values["errors"] += s.value
            elif s.name == "api_request_latency_seconds_bucket" and s.labels.get("endpoint") == endpoint:
                values["buckets"][float(s.labels["le"])] = s.value  # "+Inf" -> inf
            elif s.name == "api_model_loaded":
                values["model_loaded"] = s.value >= 1
            elif s.name == "api_model_version":
                values["model_version"] = int(s.value)
    return values


def fetch_snapshot(api_url: str | None = None, session=None, timeout: float | None = None) -> Snapshot:
    """Interroge /metrics et /health. Ne lève jamais d'exception : une API
    injoignable donne un Snapshot avec reachable=False."""
    api_url = api_url or config.API_URL
    timeout = timeout or config.HTTP_TIMEOUT_SECONDS
    http = session or requests
    now = time.time()
    try:
        resp = http.get(f"{api_url}/metrics", timeout=timeout)
        resp.raise_for_status()
        values = parse_metrics(resp.text)
    except Exception as exc:  # connexion refusée, timeout, HTTP 5xx, texte illisible
        return Snapshot(timestamp=now, reachable=False, error=str(exc))
    try:
        health_ok = http.get(f"{api_url}/health", timeout=timeout).status_code == 200
    except Exception:
        health_ok = False
    return Snapshot(timestamp=now, reachable=True, health_ok=health_ok, **values)


def histogram_quantile(q: float, buckets: dict[float, float]) -> float | None:
    """Quantile estimé à partir de buckets cumulés, comme histogram_quantile
    de Prometheus (interpolation linéaire dans le bucket concerné)."""
    if not buckets:
        return None
    bounds = sorted(buckets)
    total = buckets[bounds[-1]]  # le bucket +Inf contient toutes les requêtes
    if total <= 0:
        return None
    rank = q * total
    prev_bound, prev_count = 0.0, 0.0
    for bound in bounds:
        count = buckets[bound]
        if count >= rank:
            if math.isinf(bound):
                return prev_bound  # au-delà de la plus grande borne finie
            if count == prev_count:
                return bound
            return prev_bound + (bound - prev_bound) * (rank - prev_count) / (count - prev_count)
        prev_bound, prev_count = bound, count
    return prev_bound


def compute_window(prev: Snapshot, curr: Snapshot) -> WindowStats:
    """Différence entre deux photos = ce qui s'est passé pendant la fenêtre."""
    duration = curr.timestamp - prev.timestamp
    if not curr.reachable:
        return WindowStats(duration=duration, reachable=False, requests=0.0, errors=0.0,
                           error_rate=1.0, p95_latency=None, model_loaded=False,
                           model_version=0, health_ok=False, counter_reset=False)

    # Compteurs plus bas qu'avant = l'API a redémarré (compteurs remis à 0),
    # ou l'API était injoignable au cycle précédent : on repart de zéro.
    reset = (not prev.reachable) or curr.requests < prev.requests
    base_req = 0.0 if reset else prev.requests
    base_err = 0.0 if reset else prev.errors
    base_buckets = {} if reset else prev.buckets

    n_requests = curr.requests - base_req
    n_errors = curr.errors - base_err
    window_buckets = {le: n - base_buckets.get(le, 0.0) for le, n in curr.buckets.items()}

    return WindowStats(
        duration=duration,
        reachable=True,
        requests=n_requests,
        errors=n_errors,
        error_rate=n_errors / n_requests if n_requests > 0 else 0.0,
        p95_latency=histogram_quantile(0.95, window_buckets),
        model_loaded=curr.model_loaded,
        model_version=curr.model_version,
        health_ok=curr.health_ok,
        counter_reset=reset,
    )