from unittest.mock import Mock, patch

import pytest

from app.services.groq_service import GroqService, GroqServiceError
from app.core.groq_metrics import (
    GROQ_ERRORS_TOTAL,
    GROQ_REQUESTS_TOTAL,
    GROQ_REQUEST_DURATION_SECONDS,
    GROQ_SUCCESS_TOTAL,
    GROQ_TIMEOUTS_TOTAL,
)


def _counter_value(metric):
    return metric.collect()[0].samples[0].value


def _histogram_count(metric):
    samples = metric.collect()[0].samples

    for sample in samples:
        if sample.name.endswith("_count"):
            return sample.value

    return 0


def test_groq_success_records_metrics(monkeypatch):
    service = GroqService()

    response = Mock()
    response.choices = [
        Mock(
            message=Mock(
                content="Hello from Groq"
            )
        )
    ]

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        Mock(return_value=response),
    )

    requests_before = _counter_value(GROQ_REQUESTS_TOTAL)
    success_before = _counter_value(GROQ_SUCCESS_TOTAL)
    errors_before = _counter_value(GROQ_ERRORS_TOTAL)
    timeouts_before = _counter_value(GROQ_TIMEOUTS_TOTAL)
    duration_before = _histogram_count(
        GROQ_REQUEST_DURATION_SECONDS
    )

    result = service.generate_response(
        system_prompt="You are helpful.",
        user_message="Hello",
    )

    assert result == "Hello from Groq"

    assert _counter_value(GROQ_REQUESTS_TOTAL) == requests_before + 1
    assert _counter_value(GROQ_SUCCESS_TOTAL) == success_before + 1
    assert _counter_value(GROQ_ERRORS_TOTAL) == errors_before
    assert _counter_value(GROQ_TIMEOUTS_TOTAL) == timeouts_before
    assert (
        _histogram_count(GROQ_REQUEST_DURATION_SECONDS)
        == duration_before + 1
    )


def test_groq_timeout_records_timeout_and_error_metrics(monkeypatch):
    service = GroqService()

    from groq import APITimeoutError

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        Mock(
            side_effect=APITimeoutError(
                "timeout"
            )
        ),
    )

    requests_before = _counter_value(GROQ_REQUESTS_TOTAL)
    success_before = _counter_value(GROQ_SUCCESS_TOTAL)
    errors_before = _counter_value(GROQ_ERRORS_TOTAL)
    timeouts_before = _counter_value(GROQ_TIMEOUTS_TOTAL)
    duration_before = _histogram_count(
        GROQ_REQUEST_DURATION_SECONDS
    )

    with pytest.raises(GroqServiceError, match="timed out"):
        service.generate_response(
            system_prompt="You are helpful.",
            user_message="Hello",
        )

    assert _counter_value(GROQ_REQUESTS_TOTAL) == requests_before + 1
    assert _counter_value(GROQ_SUCCESS_TOTAL) == success_before
    assert _counter_value(GROQ_ERRORS_TOTAL) == errors_before + 1
    assert _counter_value(GROQ_TIMEOUTS_TOTAL) == timeouts_before + 1
    assert (
        _histogram_count(GROQ_REQUEST_DURATION_SECONDS)
        == duration_before + 1
    )


def test_groq_general_error_records_error_metrics(monkeypatch):
    service = GroqService()

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        Mock(
            side_effect=RuntimeError(
                "Groq unavailable"
            )
        ),
    )

    requests_before = _counter_value(GROQ_REQUESTS_TOTAL)
    success_before = _counter_value(GROQ_SUCCESS_TOTAL)
    errors_before = _counter_value(GROQ_ERRORS_TOTAL)
    timeouts_before = _counter_value(GROQ_TIMEOUTS_TOTAL)
    duration_before = _histogram_count(
        GROQ_REQUEST_DURATION_SECONDS
    )

    with pytest.raises(
        GroqServiceError,
        match="Failed to generate response",
    ):
        service.generate_response(
            system_prompt="You are helpful.",
            user_message="Hello",
        )

    assert _counter_value(GROQ_REQUESTS_TOTAL) == requests_before + 1
    assert _counter_value(GROQ_SUCCESS_TOTAL) == success_before
    assert _counter_value(GROQ_ERRORS_TOTAL) == errors_before + 1
    assert _counter_value(GROQ_TIMEOUTS_TOTAL) == timeouts_before
    assert (
        _histogram_count(GROQ_REQUEST_DURATION_SECONDS)
        == duration_before + 1
    )


def test_groq_empty_response_records_error_metric(monkeypatch):
    service = GroqService()

    response = Mock()
    response.choices = [
        Mock(
            message=Mock(
                content=""
            )
        )
    ]

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        Mock(return_value=response),
    )

    requests_before = _counter_value(GROQ_REQUESTS_TOTAL)
    success_before = _counter_value(GROQ_SUCCESS_TOTAL)
    errors_before = _counter_value(GROQ_ERRORS_TOTAL)
    duration_before = _histogram_count(
        GROQ_REQUEST_DURATION_SECONDS
    )

    with pytest.raises(
        GroqServiceError,
        match="empty response",
    ):
        service.generate_response(
            system_prompt="You are helpful.",
            user_message="Hello",
        )

    assert _counter_value(GROQ_REQUESTS_TOTAL) == requests_before + 1
    assert _counter_value(GROQ_SUCCESS_TOTAL) == success_before
    assert _counter_value(GROQ_ERRORS_TOTAL) == errors_before + 1
    assert (
        _histogram_count(GROQ_REQUEST_DURATION_SECONDS)
        == duration_before + 1
    )
