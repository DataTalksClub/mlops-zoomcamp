from agents.reliability.store import MetricsStore


def test_metrics_store_roundtrip(tmp_path):
    store = MetricsStore(f"sqlite:///{tmp_path / 'metrics.db'}")
    store.record(1_700_000_000, reachable=True, requests=20, error_rate=0.1, p95_latency=0.05,
                 probe_failure_rate=0.0, budget_consumed=0.3, degraded=False, incident_level=None)
    store.record(1_700_000_015, reachable=False, requests=0, error_rate=1.0, p95_latency=None,
                 probe_failure_rate=1.0, budget_consumed=0.6, degraded=True, incident_level="critical")
    rows = store.latest()
    assert len(rows) == 2
    assert rows[0]["incident_level"] == "critical"
    assert rows[1]["error_rate"] == 0.1
