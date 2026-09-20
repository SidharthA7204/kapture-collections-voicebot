from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import (
    get_ai_conversation_service,
)
from app.services.ai_conversation_service import (
    AIConversationService,
)
from app.services.groq_service import GroqServiceError


class FakeAIConversationService:

    def generate_response(
        self,
        user_message: str,
        current_state: str | None = None,
        conversation_history=None,
    ) -> str:
        return "I understand. How can I help you?"


class TimeoutAIConversationService:

    def generate_response(
        self,
        user_message: str,
        current_state: str | None = None,
        conversation_history=None,
    ) -> str:
        raise GroqServiceError(
            "Groq request timed out."
        )


def test_ai_chat_endpoint():
    app.dependency_overrides[
        get_ai_conversation_service
    ] = FakeAIConversationService

    client = TestClient(app)

    try:
        response = client.post(
            "/ai/chat",
            json={
                "message": "I need help with my payment.",
                "current_state": "INTENT_HANDLING",
            },
        )

        assert response.status_code == 200

        assert response.json() == {
            "response": (
                "I understand. How can I help you?"
            )
        }

    finally:
        app.dependency_overrides.clear()


def test_ai_chat_rejects_empty_message():
    app.dependency_overrides[
        get_ai_conversation_service
    ] = FakeAIConversationService

    client = TestClient(app)

    try:
        response = client.post(
            "/ai/chat",
            json={
                "message": "",
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()


def test_ai_chat_returns_503_when_ai_times_out():
    app.dependency_overrides[
        get_ai_conversation_service
    ] = TimeoutAIConversationService

    client = TestClient(app)

    try:
        response = client.post(
            "/ai/chat",
            json={
                "message": "I need help with my payment.",
            },
        )

        assert response.status_code == 503

        data = response.json()

        assert data["error"] == "AI_SERVICE_ERROR"

    finally:
        app.dependency_overrides.clear()
