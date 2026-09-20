from datetime import date
from decimal import Decimal

from app.schemas.conversation_extraction import (
    ConversationExtraction,
)
from app.schemas.intent import CustomerIntent
from app.schemas.intent_action import IntentAction
from app.services.ai_intent_service import AIIntentService
from app.services.intent_service import IntentService


def test_ai_intent_service_maps_promise_to_pay():
    service = AIIntentService(
        intent_service=IntentService(),
    )

    extraction = ConversationExtraction(
        intent=CustomerIntent.PROMISE_TO_PAY,
        amount=Decimal("5000.00"),
        promise_date=date(2026, 8, 30),
    )

    action = service.determine_action(
        extraction
    )

    assert action == IntentAction.PROMISE_TO_PAY


def test_ai_intent_service_maps_unable_to_pay():
    service = AIIntentService(
        intent_service=IntentService(),
    )

    extraction = ConversationExtraction(
        intent=CustomerIntent.UNABLE_TO_PAY,
    )

    action = service.determine_action(
        extraction
    )

    assert action == IntentAction.ASSISTANCE


def test_ai_intent_service_maps_dispute():
    service = AIIntentService(
        intent_service=IntentService(),
    )

    extraction = ConversationExtraction(
        intent=CustomerIntent.DISPUTE,
    )

    action = service.determine_action(
        extraction
    )

    assert action == IntentAction.DISPUTE
