from datetime import datetime

from app.models.call_event import CallEvent


def test_call_event_model():
    event = CallEvent(
        call_id="event_test_001",
        event_type="STATE_CHANGED",
        from_state="CALL_CONNECTED",
        to_state="INTRODUCTION",
    )

    assert event.call_id == "event_test_001"
    assert event.event_type == "STATE_CHANGED"
    assert event.from_state == "CALL_CONNECTED"
    assert event.to_state == "INTRODUCTION"

    assert event.created_at is None