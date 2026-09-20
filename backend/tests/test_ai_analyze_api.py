from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_conversation_extraction_service,
    get_ai_intent_service,
)
from app.main import app
from app.schemas.conversation_extraction import (
    ConversationExtraction,
)
from app.schemas.intent import CustomerIntent
from app.schemas.intent_action import IntentAction


def test_ai_analyze_promise_to_pay():
    extraction_service = Mock()

    extraction_service.extract.return_value = (
        ConversationExtraction(
            intent=CustomerIntent.PROMISE_TO_PAY,
            amount=Decimal("5000.00"),
            promise_date=date(2026, 8, 30),
        )
    )

    intent_service = Mock()

    intent_service.determine_action.return_value = (
        IntentAction.PROMISE_TO_PAY
    )

    app.dependency_overrides[
        get_conversation_extraction_service
    ] = lambda: extraction_service

    app.dependency_overrides[
        get_ai_intent_service
    ] = lambda: intent_service

    try:
        client = TestClient(app)

        response = client.post(
            "/ai/analyze",
            json={
                "message": (
                    "I will pay 5000 on "
                    "30 August 2026."
                )
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["extraction"]["intent"]
            == "PROMISE_TO_PAY"
        )

        assert (
            data["extraction"]["amount"]
            == "5000.00"
        )

        assert (
            data["extraction"]["promise_date"]
            == "2026-08-30"
        )

        assert (
            data["action"]
            == "PROMISE_TO_PAY"
        )

        extraction_service.extract.assert_called_once_with(
            user_message=(
                "I will pay 5000 on "
                "30 August 2026."
            )
        )

        intent_service.determine_action.assert_called_once()

    finally:
        app.dependency_overrides.clear()
