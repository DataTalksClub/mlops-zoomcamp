import requests

from agents.reliability.actions import ReliabilityActions
from agents.reliability.catalog import Action


class FakeContainer:
    def __init__(self, status="running"):
        self.status, self.restarts = status, 0

    def restart(self, timeout=10):
        self.restarts += 1
        self.status = "running"

    def start(self):
        self.status = "running"


class FakeDocker:
    def __init__(self, containers):
        self._containers = containers
        self.containers = self  # imite docker_client.containers.get(...)

    def get(self, name):
        if name not in self._containers:
            raise RuntimeError(f"No such container: {name}")
        return self._containers[name]


class FakeVersion:
    def __init__(self, version, **tags):
        self.version, self.tags = str(version), dict(tags)


class FakeMlflow:
    def __init__(self, versions, aliases):
        self.versions = {v.version: v for v in versions}
        self.aliases = dict(aliases)

    def get_model_version_by_alias(self, name, alias):
        if alias not in self.aliases:
            raise RuntimeError(f"alias {alias} introuvable")
        return self.versions[self.aliases[alias]]

    def search_model_versions(self, filter_string):
        return list(self.versions.values())

    def set_registered_model_alias(self, name, alias, version):
        self.aliases[alias] = str(version)

    def set_model_version_tag(self, name, version, key, value):
        self.versions[str(version)].tags[key] = value


class DownMlflow:
    def __getattr__(self, name):
        def fail(*args, **kwargs):
            raise ConnectionError("MLflow injoignable")
        return fail


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code, self._payload = status_code, payload or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class FakeHttp:
    def __init__(self):
        self.calls = []

    def post(self, url, json=None, timeout=None):
        self.calls.append(("POST", url))
        return FakeResponse(200, {"status": "ok"})

    def get(self, url, timeout=None):
        self.calls.append(("GET", url))
        return FakeResponse(200, {"status": "ok"})


def make(versions=None, aliases=None, containers=None):
    docker = FakeDocker(containers if containers is not None else {
        "mlops-api": FakeContainer(), "mlops-redis": FakeContainer(), "mlops-mlflow": FakeContainer()})
    mlflow = FakeMlflow(versions or [FakeVersion(3), FakeVersion(4)],
                        aliases or {"production": "4", "previous": "3"})
    http, commands = FakeHttp(), []
    actions = ReliabilityActions(docker_client=docker, mlflow_client=mlflow, http=http, runner=commands.append)
    return actions, docker, mlflow, http, commands


def test_restart_api_container():
    actions, docker, *_ = make()
    result = actions.execute(Action.RESTART_API)
    assert result.success
    assert docker.get("mlops-api").restarts == 1


def test_docker_error_is_a_result_not_an_exception():
    actions, *_ = make(containers={})
    result = actions.execute(Action.RESTART_API)
    assert result.success is False
    assert "No such container" in result.detail


def test_postgres_is_never_restarted():
    actions, *_ = make()
    result = actions.restart_container("mlops-postgres")
    assert result.success is False
    assert "autorisée" in result.detail


def test_recreate_api_uses_docker_compose():
    actions, _, _, _, commands = make()
    assert actions.execute(Action.RECREATE_API).success
    assert "--force-recreate" in commands[0]
    assert commands[0][-1] == "api"


def test_rollback_prefers_latest_healthy_version_and_flags_the_bad_one():
    versions = [FakeVersion(1, healthy="true"), FakeVersion(2, healthy="true", rolled_back="true"),
                FakeVersion(3), FakeVersion(4)]
    actions, _, mlflow, http, _ = make(versions, {"production": "4", "previous": "3"})
    result = actions.execute(Action.ROLLBACK_MODEL)
    assert result.success, result.detail
    assert mlflow.aliases["production"] == "1"          # version saine, pas une version déjà rejetée
    assert mlflow.versions["4"].tags["rolled_back"] == "true"
    assert any(url.endswith("/reload") for _, url in http.calls)


def test_rollback_falls_back_to_previous_alias():
    actions, _, mlflow, _, _ = make([FakeVersion(3), FakeVersion(4)], {"production": "4", "previous": "3"})
    assert actions.execute(Action.ROLLBACK_MODEL).success
    assert mlflow.aliases["production"] == "3"


def test_rollback_without_any_safe_version_fails_cleanly():
    actions, _, mlflow, _, _ = make([FakeVersion(4)], {"production": "4"})
    result = actions.execute(Action.ROLLBACK_MODEL)
    assert result.success is False
    assert "aucune version saine" in result.detail
    assert mlflow.aliases["production"] == "4"


def test_escalate_is_not_a_system_action():
    actions, *_ = make()
    assert actions.execute(Action.ESCALATE).success is False


def test_snapshot_then_restore_undoes_changes():
    actions, docker, mlflow, http, _ = make()
    snap = actions.take_snapshot()
    assert snap.complete and snap.production_version == "4"

    mlflow.aliases["production"] = "3"                # une tentative a changé le modèle...
    docker.get("mlops-redis").status = "exited"       # ...et arrêté Redis

    result = actions.restore(snap)
    assert result.success, result.detail
    assert mlflow.aliases["production"] == "4"
    assert docker.get("mlops-redis").status == "running"


def test_snapshot_is_incomplete_when_mlflow_is_down():
    docker = FakeDocker({"mlops-api": FakeContainer(), "mlops-redis": FakeContainer(),
                         "mlops-mlflow": FakeContainer()})
    actions = ReliabilityActions(docker_client=docker, mlflow_client=DownMlflow(), http=FakeHttp())
    assert actions.take_snapshot().complete is False