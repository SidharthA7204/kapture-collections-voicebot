from datetime import date, datetime

from app.models.customer import Customer
from app.services.customer_verification_service import (
    CustomerVerificationService,
)


def create_customer():
    return Customer(
        id=1,
        name="Test Customer",
        phone="9876543210",
        dob=datetime(1995, 5, 15),
    )


def test_verification_succeeds():
    service = CustomerVerificationService()

    customer = create_customer()

    result = service.verify(
        customer=customer,
        phone="9876543210",
        dob=date(1995, 5, 15),
    )

    assert result is True


def test_verification_fails_for_wrong_phone():
    service = CustomerVerificationService()

    customer = create_customer()

    result = service.verify(
        customer=customer,
        phone="9999999999",
        dob=date(1995, 5, 15),
    )

    assert result is False


def test_verification_fails_for_wrong_dob():
    service = CustomerVerificationService()

    customer = create_customer()

    result = service.verify(
        customer=customer,
        phone="9876543210",
        dob=date(1996, 5, 15),
    )

    assert result is False


def test_verification_fails_for_missing_customer():
    service = CustomerVerificationService()

    result = service.verify(
        customer=None,
        phone="9876543210",
        dob=date(1995, 5, 15),
    )

    assert result is False


def test_verification_fails_when_customer_has_no_dob():
    service = CustomerVerificationService()

    customer = Customer(
        id=1,
        name="Test Customer",
        phone="9876543210",
        dob=None,
    )

    result = service.verify(
        customer=customer,
        phone="9876543210",
        dob=date(1995, 5, 15),
    )

    assert result is False