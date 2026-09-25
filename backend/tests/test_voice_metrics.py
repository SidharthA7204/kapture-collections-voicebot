from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from app.core.voice_metrics import (
    VOICE_CALLS_ACTIVE,
    VOICE_CALLS_COMPLETED_TOTAL,
    VOICE_CALL_DURATION_SECONDS,
    VOICE_CALLS_STARTED_TOTAL,
)
from app.services.call_log_service import CallLogService


def _counter_value(metric):
    return metric.collect()[0].samples[0].value


def _histogram_count(metric):
    samples = metric.collect()[0].samples

    for sample in samples:
        if sample.name.endswith("_count"):
            return sample.value

    return 0


def test_start_call_records_voice_metrics():
    repository = Mock()

    call_log = Mock()
    call_log.call_id = "test-call"
    call_log.started_at = datetime.utcnow()

    repository.create.return_value = call_log

    service = CallLogService(repository)

    started_before = _counter_value(
        VOICE_CALLS_STARTED_TOTAL
    )
    active_before = _counter_value(
        VOICE_CALLS_ACTIVE
    )

    result = service.start_call(
        call_id="test-call",
        customer_id=1,
    )

    assert result == call_log

    assert (
        _counter_value(VOICE_CALLS_STARTED_TOTAL)
        == started_before + 1
    )

    assert (
        _counter_value(VOICE_CALLS_ACTIVE)
        == active_before + 1
    )

    repository.create.assert_called_once()


def test_end_call_records_completion_and_duration():
    repository = Mock()

    started_at = datetime.utcnow() - timedelta(seconds=10)

    call_log = Mock()
    call_log.call_id = "test-call"
    call_log.started_at = started_at
    call_log.ended_at = None

    repository.get_by_call_id.return_value = call_log
    repository.update.return_value = call_log

    service = CallLogService(repository)

    completed_before = _counter_value(
        VOICE_CALLS_COMPLETED_TOTAL
    )
    active_before = _counter_value(
        VOICE_CALLS_ACTIVE
    )
    duration_before = _histogram_count(
        VOICE_CALL_DURATION_SECONDS
    )

    result = service.end_call("test-call")

    assert result == call_log
    assert call_log.ended_at is not None

    assert (
        _counter_value(VOICE_CALLS_COMPLETED_TOTAL)
        == completed_before + 1
    )

    assert (
        _counter_value(VOICE_CALLS_ACTIVE)
        == active_before - 1
    )

    assert (
        _histogram_count(VOICE_CALL_DURATION_SECONDS)
        == duration_before + 1
    )

    repository.update.assert_called_once_with(call_log)


def test_end_missing_call_does_not_record_metrics():
    repository = Mock()
    repository.get_by_call_id.return_value = None

    service = CallLogService(repository)

    completed_before = _counter_value(
        VOICE_CALLS_COMPLETED_TOTAL
    )
    active_before = _counter_value(
        VOICE_CALLS_ACTIVE
    )
    duration_before = _histogram_count(
        VOICE_CALL_DURATION_SECONDS
    )

    with pytest.raises(
        ValueError,
        match="Call log not found",
    ):
        service.end_call("missing-call")

    assert (
        _counter_value(VOICE_CALLS_COMPLETED_TOTAL)
        == completed_before
    )

    assert (
        _counter_value(VOICE_CALLS_ACTIVE)
        == active_before
    )

    assert (
        _histogram_count(VOICE_CALL_DURATION_SECONDS)
        == duration_before
    )

    repository.update.assert_not_called()
