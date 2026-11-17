"""PostgresCostStore avec un vrai Postgres (psycopg 3).

Ignoré si Postgres n'est pas joignable : lancer `docker compose up -d postgres` d'abord."""
import uuid

import pytest

from agents.cost.store import PostgresCostStore
from common import config

psycopg = pytest.importorskip("psycopg")


@pytest.fixture
def conn():
    try:
        c = psycopg.connect(config.DATABASE_URL.replace("+psycopg", ""), connect_timeout=2)
    except psycopg.OperationalError:
        pytest.skip("Postgres non joignable")
    yield c
    c.close()


def test_la_connexion_reste_ouverte_et_les_couts_s_additionnent(conn):
    store = PostgresCostStore(conn)
    model = f"test-{uuid.uuid4().hex[:6]}"  # modèle unique : le test ne touche pas aux vraies données
    month = "2000-01"
    before = store.month_total(month)

    store.add(model, month, "training", 100.0, 0.05, months=1)
    store.add(model, month, "training", 300.0, 0.15, months=3)

    assert not conn.closed
    assert store.month_total(month) == pytest.approx(before + 0.20)
    assert store.by_model(month)[model] == pytest.approx(0.20)
    assert store.training_history(model) == [(100.0, 1), (300.0, 3)]