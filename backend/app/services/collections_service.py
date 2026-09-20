from decimal import Decimal

from app.schemas.collections import CollectionsSummary
from app.services.loan_service import LoanService


class CollectionsService:

    def __init__(self, loan_service: LoanService):
        self.loan_service = loan_service

    def get_customer_collections_summary(
        self,
        customer_id: int,
    ) -> CollectionsSummary:

        overdue_loans = self.loan_service.get_overdue_loans(
            customer_id
        )

        total_overdue = sum(
            (
                loan.overdue_amount
                for loan in overdue_loans
            ),
            Decimal("0.00"),
        )

        max_days_past_due = max(
            (
                loan.days_past_due
                for loan in overdue_loans
            ),
            default=0,
        )

        return CollectionsSummary(
            overdue_loan_count=len(overdue_loans),
            total_overdue_amount=total_overdue,
            max_days_past_due=max_days_past_due,
        )