from app.db.repositories.loan_repository import LoanRepository
from app.models.loan import Loan


class LoanService:

    def __init__(self, repository: LoanRepository):
        self.repository = repository

    def get_loan_by_id(
        self,
        loan_id: int,
    ) -> Loan | None:
        return self.repository.get_by_id(loan_id)

    def get_customer_loans(
        self,
        customer_id: int,
    ) -> list[Loan]:
        return self.repository.get_by_customer_id(customer_id)

    def get_overdue_loans(
        self,
        customer_id: int,
    ) -> list[Loan]:
        return self.repository.get_overdue_by_customer_id(
            customer_id
        )