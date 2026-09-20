from app.schemas.call_transition import (
    TransitionCallRequest,
    TransitionCallResponse,
)
from app.state.states import CallState


def test_transition_call_request():
    request = TransitionCallRequest(
        next_state=CallState.INTRODUCTION,
    )

    assert request.next_state == CallState.INTRODUCTION


def test_transition_call_response():
    response = TransitionCallResponse(
        call_id="call_test_001",
        current_state=CallState.INTRODUCTION,
    )

    assert response.call_id == "call_test_001"
    assert response.current_state == CallState.INTRODUCTION