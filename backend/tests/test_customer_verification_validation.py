from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.customer_verification import (
    CustomerVerificationRequest,
)


def test_phone_must_not_be_empty():
    with pytest.raises(ValidationError):
        CustomerVerificationRequest(
            phone="",
            dob=date(1995, 5, 15),
        )


def test_phone_must_contain_only_digits():
    with pytest.raises(ValidationError):
        CustomerVerificationRequest(
            phone="98765abc10",
            dob=date(1995, 5, 15),
        )


def test_phone_must_have_valid_length():
    with pytest.raises(ValidationError):
        CustomerVerificationRequest(
            phone="12345",
            dob=date(1995, 5, 15),
        )


def test_valid_verification_request_is_accepted():
    request = CustomerVerificationRequest(
        phone="9876543210",
        dob=date(1995, 5, 15),
    )

    assert request.phone == "9876543210"
    assert request.dob == date(1995, 5, 15)
