from unittest.mock import Mock

from app.core.voice_metrics import VOICE_CALLS_ENDED_TOTAL
from app.services.call_event_service import CallEventService


def _counter_value(metric):
    return metric.collect()[0].samples[0].value


def test_record_call_ended_records_voice_metric():
    repository = Mock()

    event = Mock()
    repository.create.return_value = event

    service = CallEventService(repository)

    before = _counter_value(
        VOICE_CALLS_ENDED_TOTAL
    )

    result = service.record_call_ended(
        call_id="test-call"
    )

    assert result == event

    assert (
        _counter_value(VOICE_CALLS_ENDED_TOTAL)
        == before + 1
    )

    repository.create.assert_called_once()
