import pytest

from agents.orchestrator.notifier import Notifier
from agents.orchestrator.rules import APPROVAL, AUTO, FORBIDDEN, Rules


# ---------- règles ----------
def test_rules_lit_le_fichier_autonomy():
    rules = Rules()
    assert rules.can("retrain") == AUTO
    assert rules.can("retrain_over_budget") == APPROVAL
    assert rules.can("promote_worse_model") == FORBIDDEN


def test_action_inconnue_demande_validation():
    assert Rules({}).can("supprimer_la_prod") == APPROVAL


# ---------- notifications ----------
@pytest.fixture
def notifier(tmp_path):
    return Notifier(f"sqlite:///{tmp_path / 'notif.db'}")


def test_notify_puis_latest(notifier):
    notifier.notify("Modèle v3 promu")
    last = notifier.latest()[0]
    assert last["kind"] == "info"
    assert last["text"] == "Modèle v3 promu"


def test_une_question_ne_recoit_qu_une_reponse(notifier):
    notifier.ask("On réentraîne malgré le budget ?", "req-1")
    assert notifier.latest()[0]["status"] == "pending"

    assert notifier.answer("req-1", True, "ismail") is True
    assert notifier.answer("req-1", False, "omar") is False  # double clic ignoré
    assert notifier.answer("inconnue", True, "ismail") is False

    last = notifier.latest()[0]
    assert (last["status"], last["answered_by"]) == ("approved", "ismail")
    