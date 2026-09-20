import pytest

from app.schemas.disposition import CallDisposition
from app.schemas.intent_action import IntentAction
from app.services.disposition_service import DispositionService


def test_disposition_service_can_be_created():
    service = DispositionService()

    assert service is not None


def test_payment_action_maps_to_payment_disposition():
    service = DispositionService()

    result = service.determine_disposition(
        IntentAction.PAYMENT
    )

    assert result == CallDisposition.PAYMENT_INITIATED


def test_ptp_action_maps_to_ptp_disposition():
    service = DispositionService()

    result = service.determine_disposition(
        IntentAction.PROMISE_TO_PAY
    )

    assert result == CallDisposition.PTP_COMMITTED


def test_dispute_action_maps_to_dispute_disposition():
    service = DispositionService()

    result = service.determine_disposition(
        IntentAction.DISPUTE
    )

    assert result == CallDisposition.DISPUTE_RAISED


def test_assistance_action_maps_to_negotiation():
    service = DispositionService()

    result = service.determine_disposition(
        IntentAction.ASSISTANCE
    )

    assert result == CallDisposition.NEGOTIATION_REQUIRED


def test_clarification_action_maps_to_clarification():
    service = DispositionService()

    result = service.determine_disposition(
        IntentAction.CLARIFICATION
    )

    assert result == CallDisposition.CLARIFICATION_REQUIRED