from decimal import Decimal

from app.db.repositories.loan_repository import LoanRepository
from app.models.customer import Customer
from app.models.loan import Loan
from app.services.collections_service import CollectionsService
from app.services.loan_service import LoanService


def create_customer(db_session, phone: str):
    customer = Customer(
        name="Collections Customer",
        phone=phone,
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    return customer


def test_collections_service_can_be_created(db_session):
    repository = LoanRepository(db_session)
    loan_service = LoanService(repository)

    service = CollectionsService(loan_service)

    assert service is not None


def test_collections_summary_with_overdue_loans(db_session):
    repository = LoanRepository(db_session)
    loan_service = LoanService(repository)
    service = CollectionsService(loan_service)

    customer = create_customer(
        db_session,
        "9200000001",
    )

    loans = [
        Loan(
            customer_id=customer.id,
            loan_type="PERSONAL",
            overdue_amount=Decimal("5000.00"),
            days_past_due=15,
        ),
        Loan(
            customer_id=customer.id,
            loan_type="HOME",
            overdue_amount=Decimal("7500.00"),
            days_past_due=30,
        ),
        Loan(
            customer_id=customer.id,
            loan_type="AUTO",
            overdue_amount=Decimal("0.00"),
            days_past_due=0,
        ),
    ]

    db_session.add_all(loans)
    db_session.commit()

    result = service.get_customer_collections_summary(
        customer.id
    )

    assert result.overdue_loan_count == 2
    assert result.total_overdue_amount == Decimal("12500.00")
    assert result.max_days_past_due == 30


def test_collections_summary_when_no_overdue_loans(db_session):
    repository = LoanRepository(db_session)
    loan_service = LoanService(repository)
    service = CollectionsService(loan_service)

    customer = create_customer(
        db_session,
        "9200000002",
    )

    loan = Loan(
        customer_id=customer.id,
        loan_type="PERSONAL",
        overdue_amount=Decimal("0.00"),
        days_past_due=0,
    )

    db_session.add(loan)
    db_session.commit()

    result = service.get_customer_collections_summary(
        customer.id
    )

    assert result.overdue_loan_count == 0
    assert result.total_overdue_amount == Decimal("0.00")
    assert result.max_days_past_due == 0