from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_ai_action_service,
    get_call_flow_service,
    get_conversation_extraction_service,
)
from app.main import app
from app.schemas.conversation_extraction import (
    ConversationExtraction,
)
from app.schemas.intent import CustomerIntent
from app.schemas.intent_action import IntentAction


def test_ai_execute_promise_to_pay():

    extraction_service = Mock()

    extraction_service.extract.return_value = (
        ConversationExtraction(
            intent=CustomerIntent.PROMISE_TO_PAY,
            amount=Decimal("5000.00"),
            promise_date=date(2026, 8, 30),
        )
    )

    action_service = Mock()

    action_service.intent_service.determine_action.return_value = (
        IntentAction.PROMISE_TO_PAY
    )

    action_service.execute.return_value = (
        Mock(value="PTP_COMMITTED")
    )

    call_flow_service = Mock()

    machine = Mock()

    call_flow_service.restore_machine.return_value = machine

    app.dependency_overrides[
        get_conversation_extraction_service
    ] = lambda: extraction_service

    app.dependency_overrides[
        get_ai_action_service
    ] = lambda: action_service

    app.dependency_overrides[
        get_call_flow_service
    ] = lambda: call_flow_service

    try:
        client = TestClient(app)

        response = client.post(
            "/ai/execute",
            json={
                "message": (
                    "I will pay 5000 on "
                    "30 August 2026."
                ),
                "call_id": "ai-execute-test-001",
                "customer_id": 1,
                "loan_id": 1,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["call_id"]
            == "ai-execute-test-001"
        )

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

        assert (
            data["disposition"]
            == "PTP_COMMITTED"
        )

        extraction_service.extract.assert_called_once_with(
            user_message=(
                "I will pay 5000 on "
                "30 August 2026."
            )
        )

        call_flow_service.restore_machine.assert_called_once_with(
            "ai-execute-test-001"
        )

        action_service.execute.assert_called_once()

    finally:
        app.dependency_overrides.clear()

def test_ai_execute_rejects_call_already_in_disposition():

    extraction_service = Mock()

    extraction_service.extract.return_value = (
        ConversationExtraction(
            intent=CustomerIntent.PROMISE_TO_PAY,
            amount=Decimal("5000.00"),
            promise_date=date(2026, 8, 30),
        )
    )

    action_service = Mock()

    action_service.intent_service.determine_action.return_value = (
        IntentAction.PROMISE_TO_PAY
    )

    action_service.execute.return_value = (
        Mock(value="PTP_COMMITTED")
    )

    call_flow_service = Mock()

    machine = Mock()

    machine.current_state = "DISPOSITION"

    call_flow_service.restore_machine.return_value = machine

    app.dependency_overrides[
        get_conversation_extraction_service
    ] = lambda: extraction_service

    app.dependency_overrides[
        get_ai_action_service
    ] = lambda: action_service

    app.dependency_overrides[
        get_call_flow_service
    ] = lambda: call_flow_service

    try:
        client = TestClient(app)

        response = client.post(
            "/ai/execute",
            json={
                "message": (
                    "I will pay 5000 on "
                    "30 August 2026."
                ),
                "call_id": "ai-execute-disposition-001",
                "customer_id": 1,
                "loan_id": 1,
            },
        )

        assert response.status_code == 409

        action_service.execute.assert_not_called()

    finally:
        app.dependency_overrides.clear()

def test_ai_execute_rejects_call_already_in_disposition():

    extraction_service = Mock()

    extraction_service.extract.return_value = (
        ConversationExtraction(
            intent=CustomerIntent.PROMISE_TO_PAY,
            amount=Decimal("5000.00"),
            promise_date=date(2026, 8, 30),
        )
    )

    action_service = Mock()

    action_service.intent_service.determine_action.return_value = (
        IntentAction.PROMISE_TO_PAY
    )

    action_service.execute.return_value = (
        Mock(value="PTP_COMMITTED")
    )

    call_flow_service = Mock()

    machine = Mock()

    machine.current_state = "DISPOSITION"

    call_flow_service.restore_machine.return_value = machine

    app.dependency_overrides[
        get_conversation_extraction_service
    ] = lambda: extraction_service

    app.dependency_overrides[
        get_ai_action_service
    ] = lambda: action_service

    app.dependency_overrides[
        get_call_flow_service
    ] = lambda: call_flow_service

    try:
        client = TestClient(app)

        response = client.post(
            "/ai/execute",
            json={
                "message": (
                    "I will pay 5000 on "
                    "30 August 2026."
                ),
                "call_id": "ai-execute-disposition-001",
                "customer_id": 1,
                "loan_id": 1,
            },
        )

        assert response.status_code == 409

        action_service.execute.assert_not_called()

    finally:
        app.dependency_overrides.clear()
