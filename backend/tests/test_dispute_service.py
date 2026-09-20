import pytest

from app.db.repositories.dispute_repository import DisputeRepository
from app.models.customer import Customer
from app.models.loan import Loan
from app.services.dispute_service import DisputeService


def create_customer(db_session, phone: str):
    customer = Customer(
        name="Dispute Service Customer",
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
        overdue_amount=10000,
        days_past_due=30,
    )

    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    return loan


def test_dispute_service_can_be_created(db_session):
    repository = DisputeRepository(db_session)
    service = DisputeService(repository)

    assert service is not None


def test_create_dispute(db_session):
    repository = DisputeRepository(db_session)
    service = DisputeService(repository)

    customer = create_customer(
        db_session,
        "9600000001",
    )

    loan = create_loan(
        db_session,
        customer.id,
    )

    result = service.create_dispute(
        customer_id=customer.id,
        loan_id=loan.id,
        reason="incorrect_amount",
        description="Customer says the amount is incorrect.",
    )

    assert result.id is not None
    assert result.customer_id == customer.id
    assert result.loan_id == loan.id
    assert result.reason == "INCORRECT_AMOUNT"
    assert result.description == (
        "Customer says the amount is incorrect."
    )
    assert result.status == "OPEN"


def test_create_dispute_without_loan(db_session):
    repository = DisputeRepository(db_session)
    service = DisputeService(repository)

    customer = create_customer(
        db_session,
        "9600000002",
    )

    result = service.create_dispute(
        customer_id=customer.id,
        loan_id=None,
        reason="GENERAL_COMPLAINT",
    )

    assert result.id is not None
    assert result.loan_id is None
    assert result.reason == "GENERAL_COMPLAINT"
    assert result.status == "OPEN"


def test_create_dispute_rejects_empty_reason(db_session):
    repository = DisputeRepository(db_session)
    service = DisputeService(repository)

    customer = create_customer(
        db_session,
        "9600000003",
    )

    with pytest.raises(ValueError):
        service.create_dispute(
            customer_id=customer.id,
            loan_id=None,
            reason="   ",
        )


def test_get_dispute_by_id(db_session):
    repository = DisputeRepository(db_session)
    service = DisputeService(repository)

    customer = create_customer(
        db_session,
        "9600000004",
    )

    dispute = service.create_dispute(
        customer_id=customer.id,
        loan_id=None,
        reason="payment_not_reflected",
    )

    result = service.get_dispute_by_id(dispute.id)

    assert result is not None
    assert result.id == dispute.id
    assert result.reason == "PAYMENT_NOT_REFLECTED"


def test_get_customer_disputes(db_session):
    repository = DisputeRepository(db_session)
    service = DisputeService(repository)

    customer = create_customer(
        db_session,
        "9600000005",
    )

    service.create_dispute(
        customer_id=customer.id,
        loan_id=None,
        reason="INCORRECT_AMOUNT",
    )

    service.create_dispute(
        customer_id=customer.id,
        loan_id=None,
        reason="UNKNOWN_CHARGE",
    )

    results = service.get_customer_disputes(customer.id)

    assert len(results) == 2