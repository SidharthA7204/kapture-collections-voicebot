from datetime import date
from decimal import Decimal

from app.db.repositories.promise_to_pay_repository import (
    PromiseToPayRepository,
)
from app.models.promise_to_pay import PromiseToPay


class PromiseToPayService:

    def __init__(self, repository: PromiseToPayRepository):
        self.repository = repository

    def create_promise(
        self,
        customer_id: int,
        loan_id: int,
        amount: Decimal,
        promise_date: date,
        commit: bool = True,
    ) -> PromiseToPay:

        if amount <= Decimal("0.00"):
            raise ValueError("Promise amount must be greater than zero.")

        if promise_date < date.today():
            raise ValueError("Promise date cannot be in the past.")

        promise = PromiseToPay(
            customer_id=customer_id,
            loan_id=loan_id,
            amount=amount,
            promise_date=promise_date,
            status="PENDING",
        )

        return self.repository.create(
            promise,
            commit=commit,
        )

    def get_promise_by_id(
        self,
        promise_id: int,
    ) -> PromiseToPay | None:
        return self.repository.get_by_id(promise_id)

    def get_customer_promises(
        self,
        customer_id: int,
    ) -> list[PromiseToPay]:
        return self.repository.get_by_customer_id(customer_id)
