from datetime import datetime

from app.db.repositories.call_log_repository import (
    CallLogRepository,
)
from app.db.repositories.customer_repository import (
    CustomerRepository,
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

from app.models.customer import Customer
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


def create_customer(db_session):
    customer = Customer(
        name="Termination Test Customer",
        phone="9876543210",
        dob=datetime(1995, 5, 15),
    )

    return CustomerRepository(db_session).create(
        customer
    )


def move_to_authentication(
    service,
    call_id,
    machine,
):
    for state in (
        CallState.INTRODUCTION,
        CallState.CHECK_PERSON,
        CallState.AUTHENTICATION,
    ):
        service.transition(
            call_id=call_id,
            machine=machine,
            next_state=state,
        )


def test_normal_end_call_ends_call_log(
    db_session,
):
    service = create_service(db_session)

    call_id = "termination_001"

    machine, _, _ = service.start_call(
    call_id=call_id,
    customer_id=None,
)

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    assert (
        service.call_log_service.repository
        .get_by_call_id(call_id)
        .ended_at
        is None
    )

    service.end_call(
        call_id=call_id,
        machine=machine,
    )

    call_log = (
        service.call_log_service.repository
        .get_by_call_id(call_id)
    )

    assert machine.current_state == CallState.END
    assert call_log.ended_at is not None


def test_authentication_failure_ends_call_log(
    db_session,
):
    service = create_service(db_session)

    call_id = "termination_002"

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    service.authentication_failed(
        call_id=call_id,
        machine=machine,
    )

    call_log = (
        service.call_log_service.repository
        .get_by_call_id(call_id)
    )

    assert machine.current_state == CallState.END
    assert call_log.ended_at is not None


def test_third_verification_failure_ends_call_log(
    db_session,
):
    customer = create_customer(db_session)
    service = create_service(db_session)

    call_id = "termination_003"

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=customer.id,
    )

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    for _ in range(3):
        result = service.verify_customer(
            call_id=call_id,
            machine=machine,
            phone="9999999999",
            dob=datetime(1995, 5, 15).date(),
        )

    call_log = (
        service.call_log_service.repository
        .get_by_call_id(call_id)
    )

    assert result["current_state"] == "END"


def test_repeated_end_call_is_idempotent(
    db_session,
):
    service = create_service(db_session)

    call_id = "termination_004"

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    first_result = service.end_call(
        call_id=call_id,
        machine=machine,
    )

    call_log = (
        service.call_log_service.repository
        .get_by_call_id(call_id)
    )

    first_ended_at = call_log.ended_at

    assert first_result is not None
    assert machine.current_state == CallState.END
    assert first_ended_at is not None

    # Simulate a second termination request.
    second_machine = service.restore_machine(
        call_id
    )

    second_result = service.end_call(
        call_id=call_id,
        machine=second_machine,
    )

    call_log = (
        service.call_log_service.repository
        .get_by_call_id(call_id)
    )

    assert second_result is not None
    assert second_machine.current_state == CallState.END
    assert call_log.ended_at == first_ended_at