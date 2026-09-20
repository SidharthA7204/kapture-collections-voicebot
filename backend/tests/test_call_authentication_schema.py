from app.schemas.call_authentication import (
    AuthenticateCallResponse,
)


def test_authenticate_call_response():
    response = AuthenticateCallResponse(
        call_id="call_test_001",
        authenticated=True,
        current_state="AUTHENTICATION",
    )

    assert response.call_id == "call_test_001"
    assert response.authenticated is True
    assert response.current_state == "AUTHENTICATION"