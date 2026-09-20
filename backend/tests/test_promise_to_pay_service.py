from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.db.repositories.promise_to_pay_repository import (
    PromiseToPayRepository,
)
from app.models.customer import Customer
from app.models.loan import Loan
from app.services.promise_to_pay_service import PromiseToPayService


def create_customer(db_session, phone: str):
    customer = Customer(
        name="PTP Service Customer",
        phone=phone,
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    return customer


def create_loan(db_session, customer_id: int):
    loan = Loan(
        customer_id=customer_id,
        loan_type="PERSONAL",
        overdue_amount=Decimal("15000.00"),
        days_past_due=30,
    )

    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    return loan


def test_ptp_service_can_be_created(db_session):
    repository = PromiseToPayRepository(db_session)
    service = PromiseToPayService(repository)

    assert service is not None


def test_create_promise(db_session):
    repository = PromiseToPayRepository(db_session)
    service = PromiseToPayService(repository)

    customer = create_customer(
        db_session,
        "9400000001",
    )

    loan = create_loan(
        db_session,
        customer.id,
    )

    promise_date = date.today() + timedelta(days=5)

    result = service.create_promise(
        customer_id=customer.id,
        loan_id=loan.id,
        amount=Decimal("10000.00"),
        promise_date=promise_date,
    )

    assert result.id is not None
    assert result.customer_id == customer.id
    assert result.loan_id == loan.id
    assert result.amount == Decimal("10000.00")
    assert result.promise_date == promise_date
    assert result.status == "PENDING"


def test_create_promise_rejects_zero_amount(db_session):
    repository = PromiseToPayRepository(db_session)
    service = PromiseToPayService(repository)

    customer = create_customer(
        db_session,
        "9400000002",
    )

    loan = create_loan(
        db_session,
        customer.id,
    )

    with pytest.raises(ValueError):
        service.create_promise(
            customer_id=customer.id,
            loan_id=loan.id,
            amount=Decimal("0.00"),
            promise_date=date.today() + timedelta(days=5),
        )


def test_create_promise_rejects_negative_amount(db_session):
    repository = PromiseToPayRepository(db_session)
    service = PromiseToPayService(repository)

    customer = create_customer(
        db_session,
        "9400000003",
    )

    loan = create_loan(
        db_session,
        customer.id,
    )

    with pytest.raises(ValueError):
        service.create_promise(
            customer_id=customer.id,
            loan_id=loan.id,
            amount=Decimal("-100.00"),
            promise_date=date.today() + timedelta(days=5),
        )


def test_create_promise_rejects_past_date(db_session):
    repository = PromiseToPayRepository(db_session)
    service = PromiseToPayService(repository)

    customer = create_customer(
        db_session,
        "9400000004",
    )

    loan = create_loan(
        db_session,
        customer.id,
    )

    with pytest.raises(ValueError):
        service.create_promise(
            customer_id=customer.id,
            loan_id=loan.id,
            amount=Decimal("5000.00"),
            promise_date=date.today() - timedelta(days=1),
        )


def test_get_promise_by_id(db_session):
    repository = PromiseToPayRepository(db_session)
    service = PromiseToPayService(repository)

    customer = create_customer(
        db_session,
        "9400000005",
    )

    loan = create_loan(
        db_session,
        customer.id,
    )

    promise = service.create_promise(
        customer_id=customer.id,
        loan_id=loan.id,
        amount=Decimal("7000.00"),
        promise_date=date.today() + timedelta(days=7),
    )

    result = service.get_promise_by_id(promise.id)

    assert result is not None
    assert result.id == promise.id


def test_get_customer_promises(db_session):
    repository = PromiseToPayRepository(db_session)
    service = PromiseToPayService(repository)

    customer = create_customer(
        db_session,
        "9400000006",
    )

    loan = create_loan(
        db_session,
        customer.id,
    )

    service.create_promise(
        customer_id=customer.id,
        loan_id=loan.id,
        amount=Decimal("5000.00"),
        promise_date=date.today() + timedelta(days=5),
    )

    service.create_promise(
        customer_id=customer.id,
        loan_id=loan.id,
        amount=Decimal("8000.00"),
        promise_date=date.today() + timedelta(days=10),
    )

    results = service.get_customer_promises(customer.id)

    assert len(results) == 2