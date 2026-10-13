import pytest

from agents.reliability.probes import ProbeResult, percentile, run_probes


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


class FakeSession:
    def __init__(self, statuses):
        self.statuses = list(statuses)
        self.headers_seen = []

    def post(self, url, json=None, headers=None, timeout=None):
        self.headers_seen.append(headers)
        status = self.statuses.pop(0)
        if status is None:
            raise ConnectionError("connection refused")
        return FakeResponse(status)


def test_probes_count_5xx_and_connection_errors_and_bypass_degraded_mode():
    session = FakeSession([200, 500, 503, None, 200])
    result = run_probes("http://api", count=5, session=session)
    assert result.sent == 5
    assert result.failed == 3
    assert result.ok is False
    assert all(h == {"X-Bypass-Degraded": "1"} for h in session.headers_seen)


def test_probe_result_thresholds():
    assert ProbeResult(sent=10, failed=0, p95_latency=0.02).ok
    assert not ProbeResult(sent=10, failed=1, p95_latency=0.02).ok      # 10 % > 5 %
    assert not ProbeResult(sent=10, failed=0, p95_latency=2.0).ok       # trop lent
    assert ProbeResult(sent=0, failed=0, p95_latency=None).ok           # sondes désactivées


def test_percentile_nearest_rank():
    assert percentile([0.1, 0.2, 0.3, 0.4], 0.95) == 0.4
    assert percentile([], 0.95) is None
    assert percentile([0.5], 0.95) == pytest.approx(0.5)


def test_probes_stop_early_when_the_api_is_unreachable():
    session = FakeSession([None, None, 200, 200, 200])   # 2 échecs de connexion de suite
    result = run_probes("http://api", count=5, session=session)
    assert len(session.headers_seen) == 2                  # on n'attend pas les 3 autres timeouts
    assert result.failed == 5
