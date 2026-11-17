"""Lancement : python -m agents.orchestrator (depuis prototype/).

Deux choses tournent en même temps :
- l'orchestrateur écoute Redis (dans un fil à part) ;
- la page web répond sur http://localhost:8080."""
import threading

from agents.orchestrator.agent import Orchestrator
from agents.orchestrator.notifier import Notifier
from agents.orchestrator.web import create_app
from common import config
from common.action_log import ActionLog
from common.events import EventBus

notifier = Notifier()
log = ActionLog()
orchestrator = Orchestrator(bus=EventBus(), log=log, notifier=notifier)
threading.Thread(target=orchestrator.run, daemon=True).start()

create_app(notifier, EventBus(), log).run(host="0.0.0.0", port=config.ORCHESTRATOR_WEB_PORT)