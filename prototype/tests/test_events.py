import fakeredis

from common.events import Event, EventBus, EventType, Severity


def test_event_roundtrip_json():
    event = Event(type=EventType.DRIFT_DETECTED, source="agent_qualite",
                  severity=Severity.WARNING, payload={"drift_score": 0.62})
    assert Event.from_json(event.to_json()) == event


def test_publish_and_receive():
    client = fakeredis.FakeRedis()
    bus = EventBus(client=client, channel="test.events")
    pubsub = client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("test.events")

    bus.publish(Event(type=EventType.RETRAIN_REQUESTED, source="orchestrateur"))

    message = None
    for _ in range(10):  # le premier appel peut ne rien renvoyer
        message = message or pubsub.get_message(timeout=0.2)
    received = Event.from_json(message["data"])
    assert received.type == EventType.RETRAIN_REQUESTED
    assert received.source == "orchestrateur"