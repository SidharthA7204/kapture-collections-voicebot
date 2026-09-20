from app.schemas.call import (
    StartCallRequest,
    StartCallResponse,
)


def test_start_call_request():
    request = StartCallRequest(
        call_id="call_test_001",
        customer_id=1,
    )

    assert request.call_id == "call_test_001"
    assert request.customer_id == 1


def test_start_call_request_allows_missing_customer():
    request = StartCallRequest(
        call_id="call_test_002",
    )

    assert request.call_id == "call_test_002"
    assert request.customer_id is None


def test_start_call_response():
    response = StartCallResponse(
        call_id="call_test_001",
        customer_id=1,
        current_state="CALL_CONNECTED",
        authenticated=False,
    )

    assert response.call_id == "call_test_001"
    assert response.current_state == "CALL_CONNECTED"
    assert response.authenticated is False