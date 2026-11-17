"""Lancement : python -m agents.cost (depuis prototype/).

Écoute cost_estimate et training_completed sur Redis.
Les coûts sont gardés dans Postgres (table model_costs)."""
import psycopg

from agents.cost.agent import CostAgent
from agents.cost.store import PostgresCostStore
from common import config
from common.action_log import ActionLog
from common.events import EventBus, EventType

# DATABASE_URL est au format SQLAlchemy ("postgresql+psycopg://...") : psycopg veut "postgresql://..."
conn = psycopg.connect(config.DATABASE_URL.replace("+psycopg", ""))
bus = EventBus()
agent = CostAgent(store=PostgresCostStore(conn), bus=bus, action_log=ActionLog())
print("Agent Coûts : en écoute de cost_estimate et training_completed…")
bus.listen(agent.on_event, types=[EventType.COST_ESTIMATE, EventType.TRAINING_COMPLETED])