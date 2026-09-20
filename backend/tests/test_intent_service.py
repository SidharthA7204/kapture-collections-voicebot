from app.schemas.intent import CustomerIntent
from app.schemas.intent_action import IntentAction
from app.services.intent_service import IntentService


def test_intent_service_can_be_created():
    service = IntentService()

    assert service is not None


def test_pay_now_maps_to_payment():
    service = IntentService()

    assert (
        service.determine_action(CustomerIntent.PAY_NOW)
        == IntentAction.PAYMENT
    )


def test_promise_to_pay_maps_correctly():
    service = IntentService()

    assert (
        service.determine_action(CustomerIntent.PROMISE_TO_PAY)
        == IntentAction.PROMISE_TO_PAY
    )


def test_dispute_maps_correctly():
    service = IntentService()

    assert (
        service.determine_action(CustomerIntent.DISPUTE)
        == IntentAction.DISPUTE
    )


def test_unable_to_pay_maps_to_assistance():
    service = IntentService()

    assert (
        service.determine_action(CustomerIntent.UNABLE_TO_PAY)
        == IntentAction.ASSISTANCE
    )


def test_unknown_maps_to_clarification():
    service = IntentService()

    assert (
        service.determine_action(CustomerIntent.UNKNOWN)
        == IntentAction.CLARIFICATION
    )