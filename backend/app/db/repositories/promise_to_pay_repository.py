from app.models.promise_to_pay import PromiseToPay
from sqlalchemy import select
from sqlalchemy.orm import Session


class PromiseToPayRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        promise_to_pay: PromiseToPay,
        commit: bool = True,
    ) -> PromiseToPay:
        self.db.add(promise_to_pay)

        if commit:
            self.db.commit()
            self.db.refresh(promise_to_pay)

        return promise_to_pay

    def get_by_id(
        self,
        promise_to_pay_id: int,
    ) -> PromiseToPay | None:
        statement = select(PromiseToPay).where(
            PromiseToPay.id == promise_to_pay_id
        )

        return self.db.scalar(statement)

    def get_by_customer_id(
        self,
        customer_id: int,
    ) -> list[PromiseToPay]:
        statement = select(PromiseToPay).where(
            PromiseToPay.customer_id == customer_id
        )

        return list(self.db.scalars(statement).all())
