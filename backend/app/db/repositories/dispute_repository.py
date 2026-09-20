from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dispute import Dispute


class DisputeRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        dispute: Dispute,
    ) -> Dispute:
        self.db.add(dispute)
        self.db.commit()
        self.db.refresh(dispute)

        return dispute

    def get_by_id(
        self,
        dispute_id: int,
    ) -> Dispute | None:
        statement = select(Dispute).where(
            Dispute.id == dispute_id
        )

        return self.db.scalar(statement)

    def get_by_customer_id(
        self,
        customer_id: int,
    ) -> list[Dispute]:
        statement = select(Dispute).where(
            Dispute.customer_id == customer_id
        )

        return list(self.db.scalars(statement).all())