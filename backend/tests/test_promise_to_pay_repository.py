from datetime import date
from decimal import Decimal

from app.db.repositories.promise_to_pay_repository import (
    PromiseToPayRepository,
)
from app.models.customer import Customer
from app.models.loan import Loan
from app.models.promise_to_pay import PromiseToPay


def create_customer(db_session, phone: str):
    customer = Customer(
        name="PTP Test Customer",
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


def test_ptp_repository_can_be_created(db_session):
    repository = PromiseToPayRepository(db_session)

    assert repository is not None


def test_create_ptp(db_session):
    repository = PromiseToPayRepository(db_session)

    customer = create_customer(
        db_session,
        "9300000001",
    )

    loan = create_loan(
        db_session,
        customer.id,
    )

    ptp = PromiseToPay(
        customer_id=customer.id,
        loan_id=loan.id,
        amount=Decimal("10000.00"),
        promise_date=date(2026, 8, 20),
        status="PENDING",
    )

    result = repository.create(ptp)

    assert result.id is not None
    assert result.customer_id == customer.id
    assert result.loan_id == loan.id
    assert result.amount == Decimal("10000.00")
    assert result.promise_date == date(2026, 8, 20)
    assert result.status == "PENDING"


def test_get_ptp_by_id(db_session):
    repository = PromiseToPayRepository(db_session)

    customer = create_customer(
        db_session,
        "9300000002",
    )

    loan = create_loan(
        db_session,
        customer.id,
    )

    ptp = PromiseToPay(
        customer_id=customer.id,
        loan_id=loan.id,
        amount=Decimal("8000.00"),
        promise_date=date(2026, 8, 25),
    )

    created = repository.create(ptp)

    result = repository.get_by_id(created.id)

    assert result is not None
    assert result.id == created.id
    assert result.amount == Decimal("8000.00")


def test_get_ptps_by_customer_id(db_session):
    repository = PromiseToPayRepository(db_session)

    customer = create_customer(
        db_session,
        "9300000003",
    )

    loan = create_loan(
        db_session,
        customer.id,
    )

    ptp1 = PromiseToPay(
        customer_id=customer.id,
        loan_id=loan.id,
        amount=Decimal("5000.00"),
        promise_date=date(2026, 8, 20),
    )

    ptp2 = PromiseToPay(
        customer_id=customer.id,
        loan_id=loan.id,
        amount=Decimal("7000.00"),
        promise_date=date(2026, 8, 25),
    )

    db_session.add_all([ptp1, ptp2])
    db_session.commit()

    results = repository.get_by_customer_id(
        customer.id
    )

    assert len(results) == 2
    assert all(
        ptp.customer_id == customer.id
        for ptp in results
    )