import pytest
import requests
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest

from agents.reliability.metrics import Snapshot, compute_window, fetch_snapshot, parse_metrics

BUCKETS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)


def metrics_text(ok=0, err500=0, err503=0, fast=0, slow=0, loaded=1, version=3) -> str:
    """Génère un /metrics réaliste, avec les mêmes noms que l'API."""
    reg = CollectorRegistry()
    total = Counter("api_requests_total", "t", ["endpoint", "status"], registry=reg)
    latency = Histogram("api_request_latency_seconds", "t", ["endpoint"], buckets=BUCKETS, registry=reg)
    Gauge("api_model_loaded", "t", registry=reg).set(loaded)
    Gauge("api_model_version", "t", registry=reg).set(version)
    for status, n in (("200", ok), ("500", err500), ("503", err503)):
        if n:
            total.labels("/predict", status).inc(n)
    total.labels("/health", "500").inc(7)  # autre route : doit être ignorée
    for _ in range(fast):
        latency.labels("/predict").observe(0.03)
    for _ in range(slow):
        latency.labels("/predict").observe(0.7)
    return generate_latest(reg).decode()


def snap(t, **kwargs) -> Snapshot:
    return Snapshot(timestamp=t, reachable=True, health_ok=True, **parse_metrics(metrics_text(**kwargs)))


def test_parse_counts_only_monitored_endpoint_and_5xx():
    values = parse_metrics(metrics_text(ok=8, err500=1, err503=1, fast=10, version=4))
    assert values["requests"] == 10
    assert values["errors"] == 2          # les 500 de /health sont ignorées
    assert values["model_loaded"] is True
    assert values["model_version"] == 4
    assert values["buckets"][float("inf")] == 10


def test_window_uses_deltas_between_two_snapshots():
    prev = snap(0, ok=100, fast=100)
    curr = snap(15, ok=190, err500=5, err503=5, fast=190, slow=10)
    w = compute_window(prev, curr)
    assert w.duration == 15
    assert w.requests == 100
    assert w.errors == 10
    assert w.error_rate == pytest.approx(0.10)
    # 90 requêtes à 30 ms et 10 à 700 ms : le p95 tombe dans le bucket ]0.5 ; 1.0]
    assert w.p95_latency == pytest.approx(0.75)
    assert w.counter_reset is False


def test_window_after_restart_starts_from_zero():
    prev = snap(0, ok=500, fast=500)
    curr = snap(15, ok=18, err500=2, fast=20)  # compteurs plus bas : l'API a redémarré
    w = compute_window(prev, curr)
    assert w.counter_reset is True
    assert w.requests == 20
    assert w.errors == 2


def test_window_when_api_is_unreachable():
    prev = snap(0, ok=10, fast=10)
    curr = Snapshot(timestamp=15, reachable=False, error="connection refused")
    w = compute_window(prev, curr)
    assert w.reachable is False
    assert w.error_rate == 1.0


def test_window_without_traffic():
    prev = snap(0, ok=50, fast=50)
    curr = snap(15, ok=50, fast=50)
    w = compute_window(prev, curr)
    assert w.requests == 0
    assert w.error_rate == 0.0
    assert w.p95_latency is None


class FakeResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code, self.text = status_code, text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, metrics, health_status=200):
        self.metrics, self.health_status = metrics, health_status

    def get(self, url, timeout):
        if url.endswith("/metrics"):
            return FakeResponse(text=self.metrics)
        return FakeResponse(status_code=self.health_status)


class DownSession:
    def get(self, url, timeout):
        raise requests.ConnectionError("connection refused")


def test_fetch_snapshot_reads_metrics_and_health():
    s = fetch_snapshot("http://api", session=FakeSession(metrics_text(ok=3, fast=3), health_status=503))
    assert s.reachable is True
    assert s.requests == 3
    assert s.health_ok is False


def test_fetch_snapshot_when_api_is_down():
    s = fetch_snapshot("http://api", session=DownSession())
    assert s.reachable is False
    assert "refused" in s.error