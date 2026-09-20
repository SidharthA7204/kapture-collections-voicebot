from decimal import Decimal

from app.db.repositories.loan_repository import LoanRepository
from app.models.customer import Customer
from app.models.loan import Loan


def create_customer(db_session, phone: str = "9000000001"):
    customer = Customer(
        name="Loan Test Customer",
        phone=phone,
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    return customer


def test_loan_repository_can_be_created(db_session):
    repository = LoanRepository(db_session)

    assert repository is not None


def test_create_and_get_loan_by_id(db_session):
    repository = LoanRepository(db_session)

    customer = create_customer(db_session)

    loan = Loan(
        customer_id=customer.id,
        loan_type="PERSONAL",
        overdue_amount=Decimal("12500.00"),
        days_past_due=30,
    )

    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    result = repository.get_by_id(loan.id)

    assert result is not None
    assert result.id == loan.id
    assert result.customer_id == customer.id
    assert result.overdue_amount == Decimal("12500.00")


def test_get_loans_by_customer_id(db_session):
    repository = LoanRepository(db_session)

    customer = create_customer(
        db_session,
        phone="9000000002",
    )

    loan1 = Loan(
        customer_id=customer.id,
        loan_type="PERSONAL",
        overdue_amount=Decimal("5000.00"),
        days_past_due=15,
    )

    loan2 = Loan(
        customer_id=customer.id,
        loan_type="HOME",
        overdue_amount=Decimal("10000.00"),
        days_past_due=20,
    )

    db_session.add_all([loan1, loan2])
    db_session.commit()

    results = repository.get_by_customer_id(customer.id)

    assert len(results) == 2
    assert all(
        loan.customer_id == customer.id
        for loan in results
    )


def test_get_overdue_loans_by_customer_id(db_session):
    repository = LoanRepository(db_session)

    customer = create_customer(
        db_session,
        phone="9000000003",
    )

    overdue_loan = Loan(
        customer_id=customer.id,
        loan_type="PERSONAL",
        overdue_amount=Decimal("12500.00"),
        days_past_due=30,
    )

    current_loan = Loan(
        customer_id=customer.id,
        loan_type="HOME",
        overdue_amount=Decimal("0.00"),
        days_past_due=0,
    )

    db_session.add_all([
        overdue_loan,
        current_loan,
    ])

    db_session.commit()

    results = repository.get_overdue_by_customer_id(
        customer.id
    )

    assert len(results) == 1
    assert results[0].id == overdue_loan.id
    assert results[0].overdue_amount == Decimal("12500.00")