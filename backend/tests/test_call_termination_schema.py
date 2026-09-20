from app.schemas.call_termination import (
    CallTerminationResponse,
)


def test_call_termination_response():
    response = CallTerminationResponse(
        call_id="call_test_001",
        current_state="END",
    )

    assert response.call_id == "call_test_001"
    assert response.current_state == "END"