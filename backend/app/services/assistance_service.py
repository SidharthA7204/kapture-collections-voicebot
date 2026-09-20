from app.schemas.assistance import AssistanceOutcome


class AssistanceService:

    def handle_unable_to_pay(
        self,
        customer_id: int,
        loan_id: int,
    ) -> AssistanceOutcome:
        return AssistanceOutcome.NEGOTIATION_REQUIRED