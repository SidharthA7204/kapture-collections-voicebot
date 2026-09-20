from decimal import Decimal

from app.db.repositories.loan_repository import LoanRepository
from app.models.customer import Customer
from app.models.loan import Loan
from app.services.loan_service import LoanService


def create_customer(db_session, phone: str):
    customer = Customer(
        name="Service Loan Customer",
        phone=phone,
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    return customer


def test_loan_service_can_be_created(db_session):
    repository = LoanRepository(db_session)
    service = LoanService(repository)

    assert service is not None


def test_get_loan_by_id(db_session):
    repository = LoanRepository(db_session)
    service = LoanService(repository)

    customer = create_customer(
        db_session,
        "9100000001",
    )

    loan = Loan(
        customer_id=customer.id,
        loan_type="PERSONAL",
        overdue_amount=Decimal("8000.00"),
        days_past_due=20,
    )

    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    result = service.get_loan_by_id(loan.id)

    assert result is not None
    assert result.id == loan.id


def test_get_customer_loans(db_session):
    repository = LoanRepository(db_session)
    service = LoanService(repository)

    customer = create_customer(
        db_session,
        "9100000002",
    )

    loans = [
        Loan(
            customer_id=customer.id,
            loan_type="PERSONAL",
            overdue_amount=Decimal("5000.00"),
            days_past_due=10,
        ),
        Loan(
            customer_id=customer.id,
            loan_type="HOME",
            overdue_amount=Decimal("15000.00"),
            days_past_due=30,
        ),
    ]

    db_session.add_all(loans)
    db_session.commit()

    result = service.get_customer_loans(customer.id)

    assert len(result) == 2


def test_get_overdue_loans(db_session):
    repository = LoanRepository(db_session)
    service = LoanService(repository)

    customer = create_customer(
        db_session,
        "9100000003",
    )

    overdue = Loan(
        customer_id=customer.id,
        loan_type="PERSONAL",
        overdue_amount=Decimal("12000.00"),
        days_past_due=25,
    )

    current = Loan(
        customer_id=customer.id,
        loan_type="HOME",
        overdue_amount=Decimal("0.00"),
        days_past_due=0,
    )

    db_session.add_all([overdue, current])
    db_session.commit()

    result = service.get_overdue_loans(customer.id)

    assert len(result) == 1
    assert result[0].id == overdue.id