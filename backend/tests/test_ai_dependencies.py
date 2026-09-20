from app.api.dependencies import (
    get_ai_conversation_service,
    get_groq_service,
)
from app.services.ai_conversation_service import (
    AIConversationService,
)
from app.services.groq_service import GroqService


def test_get_groq_service_returns_groq_service(
    monkeypatch,
):
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "GROQ_API_KEY",
        "test-api-key",
    )

    service = get_groq_service()

    assert isinstance(
        service,
        GroqService,
    )


def test_get_ai_conversation_service_returns_ai_service(
    monkeypatch,
):
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "GROQ_API_KEY",
        "test-api-key",
    )

    service = get_ai_conversation_service()

    assert isinstance(
        service,
        AIConversationService,
    )

    assert isinstance(
        service.groq_service,
        GroqService,
    )
