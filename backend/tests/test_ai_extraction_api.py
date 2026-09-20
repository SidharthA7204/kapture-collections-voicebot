from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_conversation_extraction_service,
)
from app.main import app
from app.schemas.conversation_extraction import (
    ConversationExtraction,
)
from app.schemas.intent import CustomerIntent


def test_ai_extract_promise_to_pay():
    service = Mock()

    service.extract.return_value = ConversationExtraction(
        intent=CustomerIntent.PROMISE_TO_PAY,
        amount=Decimal("5000.00"),
        promise_date=date(2026, 8, 30),
    )

    app.dependency_overrides[
        get_conversation_extraction_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/ai/extract",
            json={
                "message": (
                    "I will pay 5000 on 30 August 2026."
                )
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["extraction"]["intent"] == (
            "PROMISE_TO_PAY"
        )

        assert data["extraction"]["amount"] == "5000.00"

        assert data["extraction"]["promise_date"] == (
            "2026-08-30"
        )

        service.extract.assert_called_once_with(
            user_message=(
                "I will pay 5000 on 30 August 2026."
            )
        )

    finally:
        app.dependency_overrides.clear()
