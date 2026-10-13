"""Scénarios complets de l'agent Fiabilité, sans Docker, MLflow, Redis ni Postgres.

Le temps est simulé : un cycle toutes les 15 s (t = 0, 15, 30...)."""
from agents.reliability.actions import ActionResult
from agents.reliability.agent import ReliabilityAgent
from agents.reliability.catalog import Action
from agents.reliability.diagnosis import Signals
from agents.reliability.metrics import Snapshot
from agents.reliability.probes import ProbeResult
from common.events import EventType, Severity

AUTONOMY = {"restart_api": "auto", "recreate_api": "auto", "reload_model": "auto",
            "rollback_model": "auto", "degraded_mode": "auto", "restart_redis": "auto",
            "restart_mlflow": "approval"}
PROBES_OK = ProbeResult(sent=10, failed=0, p95_latency=0.02)
PROBES_KO = ProbeResult(sent=10, failed=10, p95_latency=0.02)


class Api:
    """Fausse API : compteurs cumulés, comme /metrics."""

    def __init__(self):
        self.requests = self.errors = 0.0
        self.reachable = True

    def traffic(self, ok=0, errors=0):
        self.requests += ok + errors
        self.errors += errors

    def snapshot(self):
        if not self.reachable:
            return Snapshot(timestamp=0, reachable=False, error="connection refused")
        return Snapshot(timestamp=0, reachable=True, requests=self.requests, errors=self.errors,
                        buckets={0.05: self.requests, float("inf"): self.requests},
                        model_loaded=True, model_version=4, health_ok=True)


class FakeActions:
    def __init__(self, fail=()):
        self.fail = set(fail)
        self.executed = []
        self.degraded_exits = 0

    def execute(self, action):
        self.executed.append(action)
        ok = action not in self.fail
        return ActionResult(action.value, ok, "ok" if ok else "échec simulé")

    def exit_degraded_mode(self):
        self.degraded_exits += 1
        return ActionResult("exit_degraded_mode", True, "ok")


class FakeCollector:
    def __init__(self, signals=None):
        self.signals = signals or Signals()

    def collect(self, window, now=None):
        return self.signals


class FakeBus:
    def __init__(self, broken=False):
        self.events, self.broken = [], broken

    def publish(self, event):
        if self.broken:
            raise ConnectionError("Redis injoignable")
        self.events.append(event)

    def types(self):
        return [e.type for e in self.events]


class FakeLog:
    def __init__(self):
        self.records = []

    def record(self, agent, action, model=None, details=None):
        self.records.append((action, details))


class Harness:
    """Pilote l'agent cycle par cycle."""

    def __init__(self, fail=(), signals=None, autonomy=None, bus=None):
        self.api, self.t = Api(), 0
        self.probes = PROBES_OK
        self.actions = FakeActions(fail)
        self.bus = bus or FakeBus()
        self.log = FakeLog()
        self.agent = ReliabilityAgent(bus=self.bus, action_log=self.log, actions=self.actions,
                                      collector=FakeCollector(signals), fetch=self.api.snapshot,
                                      probe=lambda: self.probes, autonomy=autonomy or AUTONOMY)
        self.agent.run_once(now=self.t)  # premier cycle : référence

    def cycle(self, ok=20, errors=0, probes=None):
        self.t += 15
        self.probes = probes or PROBES_OK
        self.api.traffic(ok=ok, errors=errors)
        return self.agent.run_once(now=self.t)

    def bad(self, n=1):
        for _ in range(n):
            self.cycle(ok=14, errors=6)   # 30 % d'erreurs

    def good(self, n=1):
        for _ in range(n):
            self.cycle(ok=20)


def test_healthy_service_stays_quiet():
    h = Harness()
    h.good(5)
    assert h.agent.incident is None
    assert h.bus.events == []


def test_a_single_spike_does_not_open_an_incident():
    h = Harness()
    h.bad(1)
    h.good(1)
    h.bad(1)
    assert h.agent.incident is None


def test_incident_opened_repaired_by_restart_then_resolved():
    h = Harness()
    h.bad(2)                                   # 2 dépassements de suite -> incident
    assert EventType.INCIDENT_OPENED in h.bus.types()
    assert h.actions.executed == [Action.RESTART_API]   # cause inconnue : 1re action du playbook
    h.good(2)                                  # 2 cycles OK de suite -> clôture
    assert h.agent.incident is None
    resolved = h.bus.events[-1]
    assert resolved.type == EventType.INCIDENT_RESOLVED
    assert resolved.payload["actions"][0]["action"] == "restart_api"
    assert resolved.payload["duration_seconds"] == 30
    assert any(action == "incident_resolved" for action, _ in h.log.records)


def test_ineffective_action_is_followed_by_the_next_one_after_the_verification_delay():
    h = Harness()
    h.bad(2)                                   # t=30 : redémarrage
    h.bad(1)                                   # t=45 : 15 s < 20 s, on attend
    assert h.actions.executed == [Action.RESTART_API]
    h.bad(1)                                   # t=60 : inefficace -> rollback
    assert h.actions.executed == [Action.RESTART_API, Action.ROLLBACK_MODEL]
    assert h.agent.incident.failed_repairs == 1


def test_everything_fails_then_human_is_notified_and_reminded():
    h = Harness(fail={Action.RESTART_API, Action.ROLLBACK_MODEL})
    h.bad(8)
    assert h.actions.executed == [Action.RESTART_API, Action.ROLLBACK_MODEL, Action.DEGRADED_MODE]
    inc = h.agent.incident
    assert inc.exhausted
    assert EventType.APPROVAL_REQUESTED in h.bus.types()

    notified = h.bus.types().count(EventType.APPROVAL_REQUESTED)
    h.bad(10)                                  # moins de 15 min : pas de relance, plus d'action
    assert h.bus.types().count(EventType.APPROVAL_REQUESTED) == notified
    assert len(h.actions.executed) == 3
    h.bad(60)                                  # 15 min plus tard : relance
    assert h.bus.types().count(EventType.APPROVAL_REQUESTED) > notified


def test_level_only_goes_up_and_failed_repairs_raise_it():
    h = Harness(fail={Action.RESTART_API, Action.ROLLBACK_MODEL})
    h.bad(2)
    first_level = h.agent.incident.level
    h.bad(6)
    levels = [Severity.INFO, Severity.WARNING, Severity.CRITICAL]
    assert levels.index(h.agent.incident.level) >= levels.index(first_level)


def test_unreachable_api_is_critical_human_notified_immediately():
    h = Harness()
    h.api.reachable = False
    h.cycle(probes=PROBES_KO)
    h.cycle(probes=PROBES_KO)
    inc = h.agent.incident
    assert inc.level == Severity.CRITICAL
    assert EventType.APPROVAL_REQUESTED in h.bus.types()       # humain prévenu dès l'ouverture
    assert h.actions.executed == [Action.RESTART_API]           # pas de mode dégradé : l'API ne répond pas


def test_critical_with_reachable_api_enables_degraded_mode_then_exits_it_on_resolution():
    h = Harness(signals=Signals(postgres_ok=False))             # Postgres touché -> critique d'office
    h.bad(2)
    inc = h.agent.incident
    assert inc.level == Severity.CRITICAL
    assert Action.DEGRADED_MODE in h.actions.executed
    assert inc.degraded
    h.good(2)
    assert h.agent.incident is None
    assert h.actions.degraded_exits == 1


def test_forbidden_action_is_skipped():
    autonomy = {**AUTONOMY, "restart_api": "forbidden"}
    h = Harness(autonomy=autonomy)
    h.bad(2)                                   # le redémarrage est interdit : non exécuté
    assert Action.RESTART_API not in h.actions.executed
    h.bad(1)
    assert h.actions.executed[0] == Action.ROLLBACK_MODEL


def test_action_needing_approval_asks_a_human_instead_of_running():
    h = Harness(autonomy={**AUTONOMY, "restart_api": "approval"})
    h.bad(2)
    assert Action.RESTART_API not in h.actions.executed
    assert any(e.payload.get("action") == "restart_api" for e in h.bus.events
               if e.type == EventType.APPROVAL_REQUESTED)


def test_mlflow_down_never_restarts_api_nor_rolls_back():
    h = Harness(signals=Signals(mlflow_ok=False))
    h.bad(4)
    assert Action.RESTART_API not in h.actions.executed
    assert Action.ROLLBACK_MODEL not in h.actions.executed


def test_restart_loop_protection():
    h = Harness(fail={Action.RESTART_API})
    agent = h.agent
    agent.restarts.extend([h.t, h.t, h.t])     # déjà 3 redémarrages dans l'heure
    h.bad(2)
    assert Action.RESTART_API not in h.actions.executed


def test_probes_detect_a_broken_model_hidden_by_degraded_traffic():
    h = Harness()
    h.cycle(ok=20, probes=PROBES_KO)           # trafic utilisateur OK (mode dégradé)...
    h.cycle(ok=20, probes=PROBES_KO)           # ...mais les sondes voient le vrai modèle cassé
    assert h.agent.incident is not None


def test_agent_survives_a_broken_bus():
    h = Harness(bus=FakeBus(broken=True))
    h.bad(2)                                   # ne doit lever aucune exception
    assert h.agent.incident is not None


# --- Non-régression : scénario observé en réel (docker stop mlops-api) ---

def test_restart_is_not_repeated_while_the_api_is_still_starting():
    h = Harness(signals=Signals(container_status="exited"))
    h.api.reachable = False
    h.cycle(probes=PROBES_KO)
    h.cycle(probes=PROBES_KO)                                   # incident api_down -> redémarrage
    assert h.actions.executed == [Action.RESTART_API]

    h.agent.collector.signals = Signals(container_status="running")   # conteneur relancé...
    h.cycle(probes=PROBES_KO)                                   # ...mais l'API charge encore le modèle
    h.cycle(probes=PROBES_KO)
    h.cycle(probes=PROBES_KO)                                   # 45 s : /health KO, on attend encore
    assert h.actions.executed == [Action.RESTART_API]           # pas de 2e redémarrage

    h.api.reachable = True                                      # l'API répond enfin
    h.good(2)
    assert h.agent.incident is None
    assert h.actions.executed == [Action.RESTART_API]           # ni 2e redémarrage, ni mode dégradé inutile


def test_after_max_wait_the_next_different_action_is_tried():
    h = Harness(signals=Signals(container_status="exited"))
    h.api.reachable = False
    for _ in range(2 + 5):                                      # ouverture puis 75 s sans réponse (> 60 s)
        h.cycle(probes=PROBES_KO)
    assert h.actions.executed == [Action.RESTART_API, Action.RECREATE_API]


def test_human_notification_is_written_to_the_action_log():
    h = Harness()
    h.api.reachable = False
    h.cycle(probes=PROBES_KO)
    h.cycle(probes=PROBES_KO)
    assert any(action == "human_notified" for action, _ in h.log.records)


def test_no_degraded_mode_while_the_restarted_api_is_warming_up():
    h = Harness(signals=Signals(container_status="exited"))
    h.api.reachable = False
    h.cycle(probes=PROBES_KO)
    h.cycle(probes=PROBES_KO)                                   # incident critique -> redémarrage
    h.agent.collector.signals = Signals(container_status="running")
    h.api.reachable = True                                      # l'API répond...
    h.cycle(ok=0, probes=PROBES_KO)                             # ...mais charge encore le modèle
    assert Action.DEGRADED_MODE not in h.actions.executed
    h.good(2)
    assert h.agent.incident is None
    assert h.actions.executed == [Action.RESTART_API]
