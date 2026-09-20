from datetime import date

from app.schemas.customer_verification import (
    CustomerVerificationRequest,
    CustomerVerificationResponse,
)


def test_customer_verification_request():
    request = CustomerVerificationRequest(
        phone="9876543210",
        dob=date(1995, 5, 15),
    )

    assert request.phone == "9876543210"
    assert request.dob == date(1995, 5, 15)


def test_customer_verification_response():
    response = CustomerVerificationResponse(
        call_id="verification_001",
        authenticated=True,
        current_state="DISCLOSE_OVERDUE",
    )

    assert response.call_id == "verification_001"
    assert response.authenticated is True
    assert response.current_state == "DISCLOSE_OVERDUE"