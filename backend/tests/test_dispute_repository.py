from app.db.repositories.dispute_repository import DisputeRepository
from app.models.customer import Customer
from app.models.dispute import Dispute
from app.models.loan import Loan


def create_customer(db_session, phone: str):
    customer = Customer(
        name="Dispute Test Customer",
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


def test_dispute_repository_can_be_created(db_session):
    repository = DisputeRepository(db_session)

    assert repository is not None


def test_create_dispute(db_session):
    repository = DisputeRepository(db_session)

    customer = create_customer(
        db_session,
        "9500000001",
    )

    loan = create_loan(
        db_session,
        customer.id,
    )

    dispute = Dispute(
        customer_id=customer.id,
        loan_id=loan.id,
        reason="INCORRECT_AMOUNT",
        description="Customer disputes the overdue amount.",
        status="OPEN",
    )

    result = repository.create(dispute)

    assert result.id is not None
    assert result.customer_id == customer.id
    assert result.loan_id == loan.id
    assert result.reason == "INCORRECT_AMOUNT"
    assert result.description == (
        "Customer disputes the overdue amount."
    )
    assert result.status == "OPEN"


def test_get_dispute_by_id(db_session):
    repository = DisputeRepository(db_session)

    customer = create_customer(
        db_session,
        "9500000002",
    )

    dispute = Dispute(
        customer_id=customer.id,
        reason="UNKNOWN_CHARGE",
        description="Customer does not recognize the charge.",
    )

    created = repository.create(dispute)

    result = repository.get_by_id(created.id)

    assert result is not None
    assert result.id == created.id
    assert result.reason == "UNKNOWN_CHARGE"


def test_get_disputes_by_customer_id(db_session):
    repository = DisputeRepository(db_session)

    customer = create_customer(
        db_session,
        "9500000003",
    )

    dispute1 = Dispute(
        customer_id=customer.id,
        reason="INCORRECT_AMOUNT",
        description="Amount appears incorrect.",
    )

    dispute2 = Dispute(
        customer_id=customer.id,
        reason="PAYMENT_NOT_REFLECTED",
        description="Previous payment is missing.",
    )

    db_session.add_all([
        dispute1,
        dispute2,
    ])

    db_session.commit()

    results = repository.get_by_customer_id(
        customer.id
    )

    assert len(results) == 2

    assert all(
        dispute.customer_id == customer.id
        for dispute in results
    )