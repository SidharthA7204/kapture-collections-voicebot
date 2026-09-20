from unittest.mock import Mock
from types import SimpleNamespace

import pytest

from app.services.ai_conversation_service import (
    AIConversationService,
)


def test_ai_conversation_rejects_empty_message():
    groq_service = Mock()

    service = AIConversationService(
        groq_service=groq_service,
    )

    with pytest.raises(ValueError):
        service.generate_response("")


def test_ai_conversation_rejects_whitespace_message():
    groq_service = Mock()

    service = AIConversationService(
        groq_service=groq_service,
    )

    with pytest.raises(ValueError):
        service.generate_response("   ")


def test_ai_conversation_delegates_to_groq():
    groq_service = Mock()

    groq_service.generate_response.return_value = (
        "I can help you with your payment."
    )

    service = AIConversationService(
        groq_service=groq_service,
    )

    result = service.generate_response(
        "I need help with my payment."
    )

    assert result == (
        "I can help you with your payment."
    )

    groq_service.generate_response.assert_called_once()

    call_kwargs = (
        groq_service.generate_response.call_args.kwargs
    )

    assert (
        call_kwargs["user_message"]
        == "I need help with my payment."
    )

    assert "authentication" in (
        call_kwargs["system_prompt"].lower()
    )

def test_ai_conversation_includes_current_call_state(
    monkeypatch,
):
    groq_service = Mock()

    groq_service.generate_response.return_value = (
        "I can help you with your payment."
    )

    service = AIConversationService(
        groq_service=groq_service,
    )

    service.generate_response(
        user_message="I need help with my payment.",
        current_state="DISCLOSE_OVERDUE",
    )

    call_kwargs = (
        groq_service.generate_response.call_args.kwargs
    )

    assert "DISCLOSE_OVERDUE" in (
        call_kwargs["system_prompt"]
    )

def test_ai_conversation_passes_history_to_groq():
    groq_service = Mock()

    groq_service.generate_response.return_value = (
        "That sounds good."
    )

    service = AIConversationService(
        groq_service=groq_service,
    )

    history = [
        {
            "role": "user",
            "content": "I cannot pay today.",
        },
        {
            "role": "assistant",
            "content": "When can you make the payment?",
        },
    ]

    result = service.generate_response(
        user_message="Next Friday.",
        current_state="INTENT_HANDLING",
        conversation_history=history,
    )

    assert result == "That sounds good."

    groq_service.generate_response.assert_called_once()

    call_kwargs = (
        groq_service.generate_response.call_args.kwargs
    )

    assert (
        call_kwargs["user_message"]
        == "Next Friday."
    )

    assert (
        call_kwargs["conversation_history"]
        == history
    )

    assert "INTENT_HANDLING" in (
        call_kwargs["system_prompt"]
    )
