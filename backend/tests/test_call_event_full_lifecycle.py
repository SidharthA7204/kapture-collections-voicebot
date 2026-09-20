from app.db.repositories.call_event_repository import (
    CallEventRepository,
)
from app.db.repositories.call_log_repository import (
    CallLogRepository,
)
from app.services.call_event_service import (
    CallEventService,
)
from app.services.call_flow_service import CallFlowService
from app.services.call_log_service import CallLogService
from app.services.collections_intent_service import (
    CollectionsIntentService,
)
from app.services.assistance_service import AssistanceService
from app.services.dispute_service import DisputeService
from app.services.disposition_service import DispositionService
from app.services.intent_service import IntentService
from app.services.payment_service import PaymentService
from app.services.promise_to_pay_service import (
    PromiseToPayService,
)
from app.services.session_service import SessionService
from app.services.customer_service import CustomerService
from app.services.customer_verification_service import (
    CustomerVerificationService,
)
from app.db.repositories.session_repository import (
    SessionRepository,
)
from app.db.repositories.dispute_repository import (
    DisputeRepository,
)
from app.db.repositories.promise_to_pay_repository import (
    PromiseToPayRepository,
)
from app.db.repositories.customer_repository import (
    CustomerRepository,
)
from app.state.states import CallState
from app.schemas.intent_action import IntentAction


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
        call_event_service=CallEventService(
            CallEventRepository(db_session)
        ),
    )


def test_successful_call_creates_ordered_audit_trail(
    db_session,
):
    call_id = "audit_lifecycle_001"

    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    service.transition(
        call_id=call_id,
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id=call_id,
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id=call_id,
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    service.authenticate(
        call_id=call_id,
        machine=machine,
    )

    service.transition(
        call_id=call_id,
        machine=machine,
        next_state=CallState.INTENT_HANDLING,
    )

    service.handle_action(
        call_id=call_id,
        machine=machine,
        action=IntentAction.PAYMENT,
    )

    service.end_call(
        call_id=call_id,
        machine=machine,
    )

    events = (
        CallEventRepository(db_session)
        .get_by_call_id(call_id)
    )

    assert len(events) == 9

    assert [
        event.event_type
        for event in events
    ] == [
    "STATE_CHANGED",
    "STATE_CHANGED",
    "STATE_CHANGED",
    "AUTHENTICATION",
    "STATE_CHANGED",
    "STATE_CHANGED",
    "STATE_CHANGED",
    "STATE_CHANGED",
    "CALL_ENDED",
]

    assert (
        events[0].from_state
        == "CALL_CONNECTED"
    )
    assert events[0].to_state == "INTRODUCTION"

    assert (
        events[1].from_state
        == "INTRODUCTION"
    )
    assert events[1].to_state == "CHECK_PERSON"

    assert (
        events[2].from_state
        == "CHECK_PERSON"
    )
    assert events[2].to_state == "AUTHENTICATION"

    assert (
        events[3].event_type
        == "AUTHENTICATION"
    )
    assert (
        events[3].from_state
        == "AUTHENTICATION"
    )
    assert (
        events[3].to_state
        == "DISCLOSE_OVERDUE"
    )

    assert (
        events[4].from_state
        == "AUTHENTICATION"
    )
    assert (
        events[4].to_state
        == "DISCLOSE_OVERDUE"
    )

    assert (
        events[5].from_state
        == "DISCLOSE_OVERDUE"
    )
    assert (
        events[5].to_state
        == "INTENT_HANDLING"
    )

    assert (
        events[6].from_state
        == "INTENT_HANDLING"
    )
    assert (
        events[6].to_state
        == "DISPOSITION"
    )

    assert (
        events[7].from_state
        == "DISPOSITION"
    )
    assert events[7].to_state == "END"

    assert (
        events[8].event_type
        == "CALL_ENDED"
    )
    assert events[8].to_state == "END"
