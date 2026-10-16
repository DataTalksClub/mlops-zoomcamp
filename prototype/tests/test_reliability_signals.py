from agents.reliability.metrics import WindowStats
from agents.reliability.signals import ModelAgeTracker, SignalCollector, cpu_percent, memory_percent

STATS = {
    "memory_stats": {"usage": 600, "limit": 1000, "stats": {"inactive_file": 100}},
    "cpu_stats": {"cpu_usage": {"total_usage": 3000}, "system_cpu_usage": 20000, "online_cpus": 2},
    "precpu_stats": {"cpu_usage": {"total_usage": 1000}, "system_cpu_usage": 10000},
}


def win(version=4, reachable=True):
    return WindowStats(duration=15, reachable=reachable, requests=100, errors=0, error_rate=0.0,
                       p95_latency=0.05, model_loaded=True, model_version=version, health_ok=True,
                       counter_reset=False)


class FakeContainer:
    def __init__(self, status="running", restart_count=0):
        self.status = status
        self.attrs = {"RestartCount": restart_count}

    def stats(self, stream=False):
        return STATS


class FakeDocker:
    def __init__(self, container=None):
        self.container = container
        self.containers = self

    def get(self, name):
        if self.container is None:
            raise RuntimeError("Docker injoignable")
        return self.container


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


class OkHttp:
    def get(self, url, timeout=None):
        return FakeResponse(200)


class DownHttp:
    def get(self, url, timeout=None):
        raise ConnectionError("MLflow injoignable")


class FakeRedis:
    def __init__(self, up=True):
        self.up = up

    def ping(self):
        if not self.up:
            raise ConnectionError("Redis injoignable")
        return True


def postgres_down():
    raise ConnectionError("Postgres injoignable")


def collector(container=FakeContainer(), http=OkHttp(), redis_up=True, postgres=lambda: None):
    return SignalCollector(docker_client=FakeDocker(container), http=http,
                           redis_client=FakeRedis(redis_up), postgres_check=postgres)


def test_resource_percentages_like_docker_stats():
    assert memory_percent(STATS) == 50.0   # (600 - 100) / 1000
    assert cpu_percent(STATS) == 40.0      # 2000 / 10000 * 2 CPU
    assert cpu_percent({}) is None


def test_all_green():
    s = collector().collect(win(), now=0)
    assert s.container_status == "running"
    assert s.memory_percent == 50.0
    assert s.mlflow_ok and s.redis_ok and s.postgres_ok
    assert s.restarts_recent == 0


def test_crash_loop_counts_restarts_over_ten_minutes():
    container = FakeContainer(restart_count=2)
    c = collector(container=container)
    c.collect(win(), now=0)
    container.attrs["RestartCount"] = 5
    assert c.collect(win(), now=60).restarts_recent == 3
    assert c.collect(win(), now=700).restarts_recent == 0   # mesure de t=0 sortie de la fenêtre


def test_failing_probes_never_raise():
    s = collector(http=DownHttp(), redis_up=False, postgres=postgres_down).collect(win(), now=0)
    assert s.mlflow_ok is False
    assert s.redis_ok is False
    assert s.postgres_ok is False


def test_docker_unreachable():
    s = SignalCollector(docker_client=FakeDocker(None), http=OkHttp(), redis_client=FakeRedis(),
                        postgres_check=lambda: None).collect(win(), now=0)
    assert s.container_status == "unknown"


def test_model_age_is_unknown_until_a_version_change_is_observed():
    t = ModelAgeTracker()
    assert t.update(4, now=0) is None        # 1re observation : on ne sait pas depuis quand
    assert t.update(4, now=100) is None
    assert t.update(5, now=200) == 0         # changement observé
    assert t.update(5, now=500) == 300

def test_observe_tracks_versions_between_incidents():
    c = collector()
    c.observe(win(version=4), now=0)        # observé à chaque cycle, sans incident
    c.observe(win(version=5), now=100)      # promotion vue
    assert c.collect(win(version=5), now=160).model_age_seconds == 60


def test_version_restored_by_the_agent_is_not_suspected():
    t = ModelAgeTracker()
    t.update(1, now=0)
    t.update(3, now=100)                    # promotion (suspecte)
    assert t.update(3, now=160) == 60
    t.trust_next_change()                   # l'agent fait un rollback vers la v1
    assert t.update(1, now=200) is None     # la v1 restaurée n'est pas une "nouvelle" version


def test_api_without_model_does_not_count_as_a_version_change():
    t = ModelAgeTracker()
    t.update(1, now=0)
    t.update(0, now=50)                     # API redémarrée sans modèle (version 0)
    assert t.update(1, now=100) is None     # retour de la v1 : pas un changement
