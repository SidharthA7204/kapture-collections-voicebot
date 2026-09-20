from app.db.repositories.dispute_repository import DisputeRepository
from app.models.dispute import Dispute


class DisputeService:

    def __init__(self, repository: DisputeRepository):
        self.repository = repository

    def create_dispute(
        self,
        customer_id: int,
        loan_id: int | None,
        reason: str,
        description: str | None = None,
    ) -> Dispute:

        normalized_reason = reason.strip().upper()

        if not normalized_reason:
            raise ValueError("Dispute reason is required.")

        dispute = Dispute(
            customer_id=customer_id,
            loan_id=loan_id,
            reason=normalized_reason,
            description=description,
            status="OPEN",
        )

        return self.repository.create(dispute)

    def get_dispute_by_id(
        self,
        dispute_id: int,
    ) -> Dispute | None:
        return self.repository.get_by_id(dispute_id)

    def get_customer_disputes(
        self,
        customer_id: int,
    ) -> list[Dispute]:
        return self.repository.get_by_customer_id(customer_id)