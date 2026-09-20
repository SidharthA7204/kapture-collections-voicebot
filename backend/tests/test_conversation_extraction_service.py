from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from app.schemas.intent import CustomerIntent
from app.services.conversation_extraction_service import (
    ConversationExtractionService,
)


def test_extract_promise_to_pay():
    groq = Mock()

    groq.generate_response.return_value = """
{
    "intent": "PROMISE_TO_PAY",
    "amount": "5000.00",
    "promise_date": "2026-08-30"
}
"""

    service = ConversationExtractionService(
        groq_service=groq,
    )

    result = service.extract(
        "I will pay 5000 on 30 August 2026."
    )

    assert result.intent == CustomerIntent.PROMISE_TO_PAY
    assert result.amount == Decimal("5000.00")
    assert result.promise_date == date(2026, 8, 30)


def test_extract_unknown_payment_details():
    groq = Mock()

    groq.generate_response.return_value = """
{
    "intent": "UNABLE_TO_PAY",
    "amount": null,
    "promise_date": null
}
"""

    service = ConversationExtractionService(
        groq_service=groq,
    )

    result = service.extract(
        "I don't have enough money right now."
    )

    assert result.intent == CustomerIntent.UNABLE_TO_PAY
    assert result.amount is None
    assert result.promise_date is None
