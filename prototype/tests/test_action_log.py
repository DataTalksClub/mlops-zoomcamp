from common.action_log import ActionLog


def test_record_and_read(tmp_path):
    log = ActionLog(url=f"sqlite:///{tmp_path / 'log.db'}")
    log.record("agent_retrain", "model_promoted", model="taxi-duration", details={"version": "2"})
    rows = log.latest()
    assert rows[0]["action"] == "model_promoted"
    assert rows[0]["details"] == {"version": "2"}