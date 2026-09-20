from app.db.repositories.call_event_repository import (
    CallEventRepository,
)
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
from app.services.call_event_service import (
    CallEventService,
)
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
from app.state.states import CallState


def create_service(db_session):
    session_service = SessionService(
        SessionRepository(db_session)
    )

    call_log_service = CallLogService(
        CallLogRepository(db_session)
    )

    call_event_service = CallEventService(
        CallEventRepository(db_session)
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
        call_event_service=call_event_service,
    )


def test_state_transition_creates_audit_event(
    db_session,
):
    call_id = "audit_integration_001"

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

    events = (
        CallEventRepository(db_session)
        .get_by_call_id(call_id)
    )

    assert len(events) == 1

    event = events[0]

    assert event.event_type == "STATE_CHANGED"
    assert event.from_state == "CALL_CONNECTED"
    assert event.to_state == "INTRODUCTION"


def test_multiple_state_transitions_create_ordered_events(
    db_session,
):
    call_id = "audit_integration_002"

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

    events = (
        CallEventRepository(db_session)
        .get_by_call_id(call_id)
    )

    assert len(events) == 3

    assert (
        events[0].from_state
        == "CALL_CONNECTED"
    )
    assert (
        events[0].to_state
        == "INTRODUCTION"
    )

    assert (
        events[1].from_state
        == "INTRODUCTION"
    )
    assert (
        events[1].to_state
        == "CHECK_PERSON"
    )

    assert (
        events[2].from_state
        == "CHECK_PERSON"
    )
    assert (
        events[2].to_state
        == "AUTHENTICATION"
    )

def test_authentication_creates_audit_event(
    db_session,
):
    call_id = "audit_auth_001"

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

    events = (
        CallEventRepository(db_session)
        .get_by_call_id(call_id)
    )

    authentication_events = [
        event
        for event in events
        if event.event_type == "AUTHENTICATION"
    ]

    assert len(authentication_events) == 1

    event = authentication_events[0]

    assert event.from_state == "AUTHENTICATION"
    assert event.to_state == "DISCLOSE_OVERDUE"

    assert machine.current_state == (
        CallState.DISCLOSE_OVERDUE
    )

def test_authentication_failed_creates_audit_event(
    db_session,
):
    call_id = "audit_auth_002"

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

    service.authentication_failed(
        call_id=call_id,
        machine=machine,
    )

    events = (
        CallEventRepository(db_session)
        .get_by_call_id(call_id)
    )

    authentication_events = [
        event
        for event in events
        if event.event_type
        == "AUTHENTICATION_FAILED"
    ]

    assert len(authentication_events) == 1

    event = authentication_events[0]

    assert event.from_state == "AUTHENTICATION"
    assert event.to_state == "END"

    assert machine.current_state == CallState.END

def test_verification_success_creates_audit_event(
    db_session,
):
    from datetime import datetime

    from app.models.customer import Customer

    call_id = "audit_verify_success_001"

    customer = Customer(
        name="Audit Verification Customer",
        phone="9876543210",
        dob=datetime(1995, 5, 15),
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=customer.id,
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

    result = service.verify_customer(
        call_id=call_id,
        machine=machine,
        phone="9876543210",
        dob=datetime(1995, 5, 15).date(),
    )

    assert result["authenticated"] is True
    assert result["current_state"] == "DISCLOSE_OVERDUE"

    events = (
        CallEventRepository(db_session)
        .get_by_call_id(call_id)
    )

    verification_events = [
        event
        for event in events
        if event.event_type
        == "VERIFICATION_SUCCESS"
    ]

    assert len(verification_events) == 1

    event = verification_events[0]

    assert event.from_state == "AUTHENTICATION"
    assert event.to_state == "DISCLOSE_OVERDUE"