from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from app.schemas.conversation_extraction import (
    ConversationExtraction,
)
from app.schemas.intent import CustomerIntent
from app.schemas.intent_action import IntentAction
from app.services.ai_action_service import AIActionService


def test_ai_action_service_executes_ptp():
    intent_service = Mock()
    call_flow_service = Mock()
    machine = Mock()

    intent_service.determine_action.return_value = (
        IntentAction.PROMISE_TO_PAY
    )

    call_flow_service.handle_action.return_value = (
        Mock(value="PTP_COMMITTED")
    )

    service = AIActionService(
        intent_service=intent_service,
        call_flow_service=call_flow_service,
    )

    extraction = ConversationExtraction(
        intent=CustomerIntent.PROMISE_TO_PAY,
        amount=Decimal("5000.00"),
        promise_date=date(2026, 8, 30),
    )

    result = service.execute(
        call_id="ai-ptp-test-001",
        customer_id=1,
        loan_id=1,
        machine=machine,
        extraction=extraction,
    )

    intent_service.determine_action.assert_called_once_with(
        extraction
    )

    call_flow_service.handle_action.assert_called_once_with(
        call_id="ai-ptp-test-001",
        machine=machine,
        action=IntentAction.PROMISE_TO_PAY,
        customer_id=1,
        loan_id=1,
        amount=Decimal("5000.00"),
        promise_date=date(2026, 8, 30),
    )

    assert result.value == "PTP_COMMITTED"


def test_ai_action_service_executes_dispute():
    intent_service = Mock()
    call_flow_service = Mock()
    machine = Mock()

    intent_service.determine_action.return_value = (
        IntentAction.DISPUTE
    )

    call_flow_service.handle_action.return_value = (
        Mock(value="DISPUTE_RAISED")
    )

    service = AIActionService(
        intent_service=intent_service,
        call_flow_service=call_flow_service,
    )

    extraction = ConversationExtraction(
        intent=CustomerIntent.DISPUTE,
    )

    result = service.execute(
        call_id="ai-dispute-test-001",
        customer_id=1,
        loan_id=1,
        machine=machine,
        extraction=extraction,
    )

    call_flow_service.handle_action.assert_called_once_with(
        call_id="ai-dispute-test-001",
        machine=machine,
        action=IntentAction.DISPUTE,
        customer_id=1,
        loan_id=1,
        amount=None,
        promise_date=None,
    )

    assert result.value == "DISPUTE_RAISED"
