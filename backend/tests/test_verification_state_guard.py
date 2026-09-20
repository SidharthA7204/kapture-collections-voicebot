import pytest

from app.db.repositories.call_log_repository import (
    CallLogRepository,
)
from app.db.repositories.dispute_repository import (
    DisputeRepository,
)
from app.db.repositories.promise_to_pay_repository import (
    PromiseToPayRepository,
)
from app.db.repositories.session_repository import (
    SessionRepository,
)
from app.db.repositories.customer_repository import (
    CustomerRepository,
)


from app.services.assistance_service import AssistanceService
from app.services.call_flow_service import CallFlowService
from app.services.call_log_service import CallLogService
from app.services.collections_intent_service import (
    CollectionsIntentService,
)
from app.services.customer_service import CustomerService
from app.services.customer_verification_service import (
    CustomerVerificationService,
)
from app.services.dispute_service import DisputeService
from app.services.disposition_service import DispositionService
from app.services.intent_service import IntentService
from app.services.payment_service import PaymentService
from app.services.promise_to_pay_service import (
    PromiseToPayService,
)
from app.services.session_service import SessionService
from app.state.state_machine import InvalidStateTransition
from app.state.states import CallState


def create_service(db_session):
    session_service = SessionService(
        SessionRepository(db_session)
    )

    call_log_service = CallLogService(
        CallLogRepository(db_session)
    )

    collections_intent_service = (
        CollectionsIntentService(
            intent_service=IntentService(),
            dispute_service=DisputeService(
                DisputeRepository(db_session)
            ),
            promise_to_pay_service=PromiseToPayService(
                PromiseToPayRepository(db_session)
            ),
            payment_service=PaymentService(),
            assistance_service=AssistanceService(),
            disposition_service=DispositionService(),
            call_log_service=call_log_service,
        )
    )

    return CallFlowService(
        session_service=session_service,
        call_log_service=call_log_service,
        collections_intent_service=(
            collections_intent_service
        ),
        customer_service=CustomerService(
            CustomerRepository(db_session)
        ),
        customer_verification_service=(
            CustomerVerificationService()
        ),
    )


def test_verification_requires_authentication_state(
    db_session,
):
    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id="verification_guard_001",
        customer_id=None,
    )

    with pytest.raises(InvalidStateTransition):
        service.verify_customer(
            call_id="verification_guard_001",
            machine=machine,
            phone="9876543210",
            dob=__import__("datetime").date(
                1995,
                5,
                15,
            ),
        )


def test_verification_allowed_during_authentication(
    db_session,
):
    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id="verification_guard_002",
        customer_id=None,
    )

    service.transition(
        call_id="verification_guard_002",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="verification_guard_002",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="verification_guard_002",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    result = service.verify_customer(
        call_id="verification_guard_002",
        machine=machine,
        phone="9876543210",
        dob=__import__("datetime").date(
            1995,
            5,
            15,
        ),
    )

    assert result["authenticated"] is False
    assert result["current_state"] == "AUTHENTICATION"
