from app.schemas.assistance import AssistanceOutcome
from app.services.assistance_service import AssistanceService


def test_assistance_service_can_be_created():
    service = AssistanceService()

    assert service is not None


def test_unable_to_pay_requires_negotiation():
    service = AssistanceService()

    result = service.handle_unable_to_pay(
        customer_id=1,
        loan_id=1,
    )

    assert result == AssistanceOutcome.NEGOTIATION_REQUIRED