from types import SimpleNamespace

import pytest

from app.services.groq_service import (
    GroqService,
    GroqServiceError,
)


def test_groq_service_requires_api_key(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "GROQ_API_KEY",
        "",
    )

    with pytest.raises(ValueError):
        GroqService()


def test_groq_service_uses_configured_model(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "GROQ_API_KEY",
        "test-api-key",
    )

    monkeypatch.setattr(
        settings,
        "GROQ_MODEL",
        "test-model",
    )

    service = GroqService()

    assert service.model == "test-model"


def test_groq_service_uses_configured_timeout(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "GROQ_API_KEY",
        "test-api-key",
    )

    monkeypatch.setattr(
        settings,
        "GROQ_TIMEOUT_SECONDS",
        15.0,
    )

    service = GroqService()

    assert service.client.timeout == 15.0


def test_generate_response_returns_groq_content(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "GROQ_API_KEY",
        "test-api-key",
    )

    service = GroqService()

    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="Hello, how can I help you?"
                    )
                )
            ]
        )

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        fake_create,
    )

    result = service.generate_response(
        system_prompt="You are a collections voice agent.",
        user_message="I need help with my payment.",
    )

    assert result == "Hello, how can I help you?"

    assert captured["model"] == settings.GROQ_MODEL

    assert captured["messages"] == [
        {
            "role": "system",
            "content": "You are a collections voice agent.",
        },
        {
            "role": "user",
            "content": "I need help with my payment.",
        },
    ]


def test_groq_service_raises_controlled_error_on_api_failure(
    monkeypatch,
):
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "GROQ_API_KEY",
        "test-api-key",
    )

    service = GroqService()

    def fake_create(**kwargs):
        raise RuntimeError("Groq API unavailable")

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        fake_create,
    )

    with pytest.raises(GroqServiceError):
        service.generate_response(
            system_prompt="Test",
            user_message="Hello",
        )


def test_groq_service_raises_controlled_error_on_timeout(
    monkeypatch,
):
    from app.core.config import settings
    from groq import APITimeoutError

    monkeypatch.setattr(
        settings,
        "GROQ_API_KEY",
        "test-api-key",
    )

    service = GroqService()

    def fake_create(**kwargs):
        raise APITimeoutError(
            "Groq request timed out."
        )

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        fake_create,
    )

    with pytest.raises(
        GroqServiceError,
        match="Groq request timed out",
    ):
        service.generate_response(
            system_prompt="Test",
            user_message="Hello",
        )


def test_groq_service_rejects_empty_response(
    monkeypatch,
):
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "GROQ_API_KEY",
        "test-api-key",
    )

    service = GroqService()

    def fake_create(**kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=""
                    )
                )
            ]
        )

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        fake_create,
    )

    with pytest.raises(GroqServiceError):
        service.generate_response(
            system_prompt="Test",
            user_message="Hello",
        )
