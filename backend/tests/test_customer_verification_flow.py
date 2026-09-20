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


def move_to_authentication(
    service,
    call_id,
    machine,
):
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


def create_customer(db_session):
    customer = Customer(
        name="Verification Customer",
        phone="9876543210",
        dob=datetime(1995, 5, 15),
    )

    return CustomerRepository(db_session).create(
        customer
    )


def test_successful_customer_verification(
    db_session,
):
    customer = create_customer(db_session)

    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id="verification_flow_001",
        customer_id=customer.id,
    )

    move_to_authentication(
        service,
        "verification_flow_001",
        machine,
    )

    result = service.verify_customer(
        call_id="verification_flow_001",
        machine=machine,
        phone="9876543210",
        dob=datetime(1995, 5, 15).date(),
    )

    assert result["authenticated"] is True
    assert (
        result["current_state"]
        == "DISCLOSE_OVERDUE"
    )


def test_wrong_phone_fails_verification(
    db_session,
):
    customer = create_customer(db_session)

    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id="verification_flow_002",
        customer_id=customer.id,
    )

    move_to_authentication(
        service,
        "verification_flow_002",
        machine,
    )

    result = service.verify_customer(
        call_id="verification_flow_002",
        machine=machine,
        phone="9999999999",
        dob=datetime(1995, 5, 15).date(),
    )

    assert result["authenticated"] is False
    assert result["current_state"] == "AUTHENTICATION"


def test_wrong_dob_fails_verification(
    db_session,
):
    customer = create_customer(db_session)

    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id="verification_flow_003",
        customer_id=customer.id,
    )

    move_to_authentication(
        service,
        "verification_flow_003",
        machine,
    )

    result = service.verify_customer(
        call_id="verification_flow_003",
        machine=machine,
        phone="9876543210",
        dob=datetime(1996, 5, 15).date(),
    )

    assert result["authenticated"] is False
    assert result["current_state"] == "AUTHENTICATION"


def test_missing_customer_fails_verification(
    db_session,
):
    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id="verification_flow_004",
        customer_id=None,
    )

    move_to_authentication(
        service,
        "verification_flow_004",
        machine,
    )

    result = service.verify_customer(
        call_id="verification_flow_004",
        machine=machine,
        phone="9876543210",
        dob=datetime(1995, 5, 15).date(),
    )

    assert result["authenticated"] is False
    assert result["current_state"] == "AUTHENTICATION"
