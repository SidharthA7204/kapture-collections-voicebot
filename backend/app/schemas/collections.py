from decimal import Decimal

from pydantic import BaseModel


class CollectionsSummary(BaseModel):
    overdue_loan_count: int
    total_overdue_amount: Decimal
    max_days_past_due: int