from decimal import Decimal

import pytest

from app.schemas.payment import PaymentStatus
from app.services.payment_service import PaymentService


def test_payment_service_can_be_created():
    service = PaymentService()

    assert service is not None


def test_payment_can_be_initiated():
    service = PaymentService()

    result = service.initiate_payment(
        customer_id=1,
        loan_id=1,
        amount=Decimal("5000.00"),
    )

    assert result == PaymentStatus.INITIATED


def test_payment_rejects_zero_amount():
    service = PaymentService()

    with pytest.raises(ValueError):
        service.initiate_payment(
            customer_id=1,
            loan_id=1,
            amount=Decimal("0.00"),
        )


def test_payment_rejects_negative_amount():
    service = PaymentService()

    with pytest.raises(ValueError):
        service.initiate_payment(
            customer_id=1,
            loan_id=1,
            amount=Decimal("-100.00"),
        )