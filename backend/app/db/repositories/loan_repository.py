from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.loan import Loan


class LoanRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, loan_id: int) -> Loan | None:
        statement = select(Loan).where(
            Loan.id == loan_id
        )

        return self.db.scalar(statement)

    def get_by_customer_id(
        self,
        customer_id: int,
    ) -> list[Loan]:
        statement = select(Loan).where(
            Loan.customer_id == customer_id
        )

        return list(self.db.scalars(statement).all())

    def get_overdue_by_customer_id(
        self,
        customer_id: int,
    ) -> list[Loan]:
        statement = select(Loan).where(
            Loan.customer_id == customer_id,
            Loan.overdue_amount > 0,
        )

        return list(self.db.scalars(statement).all())