from app.schemas.call_action import (
    CallActionRequest,
    CallActionResponse,
)
from app.schemas.intent_action import IntentAction


def test_call_action_request():
    request = CallActionRequest(
        action=IntentAction.PAYMENT,
    )

    assert request.action == IntentAction.PAYMENT


def test_call_action_response():
    response = CallActionResponse(
        call_id="call_test_001",
        disposition="PAYMENT_INITIATED",
    )

    assert response.call_id == "call_test_001"
    assert response.disposition == "PAYMENT_INITIATED"