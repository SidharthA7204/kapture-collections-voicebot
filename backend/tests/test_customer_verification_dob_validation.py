from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.customer_verification import (
    CustomerVerificationRequest,
)


def test_dob_cannot_be_in_the_future():
    with pytest.raises(ValidationError):
        CustomerVerificationRequest(
            phone="9876543210",
            dob=date(2099, 1, 1),
        )


def test_dob_cannot_be_too_old():
    with pytest.raises(ValidationError):
        CustomerVerificationRequest(
            phone="9876543210",
            dob=date(1800, 1, 1),
        )


def test_valid_dob_is_accepted():
    request = CustomerVerificationRequest(
        phone="9876543210",
        dob=date(1995, 5, 15),
    )

    assert request.dob == date(1995, 5, 15)
