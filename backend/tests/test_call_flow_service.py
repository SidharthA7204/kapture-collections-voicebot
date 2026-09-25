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

from app.models.customer import Customer
from app.models.loan import Loan
from app.models.customer import Customer
from app.schemas.intent_action import IntentAction

from app.services.assistance_service import AssistanceService
from app.services.call_flow_service import CallFlowService
from app.services.call_log_service import CallLogService
from app.services.collections_intent_service import (
    CollectionsIntentService,
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
import pytest

from app.state.state_machine import InvalidStateTransition
from datetime import date, timedelta
from decimal import Decimal

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
    )
def test_start_call_creates_session_and_call_log(
    db_session,
):
    service = create_service(db_session)

    machine, session, call_log = service.start_call(
        call_id="flow_test_001",
        customer_id=None,
    )

    assert machine.current_state == CallState.CALL_CONNECTED
    assert session.call_id == "flow_test_001"
    assert session.current_state == "CALL_CONNECTED"
    assert call_log.call_id == "flow_test_001"
    assert call_log.started_at is not None
def test_authenticate_updates_session_and_state(
    db_session,
):
    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id="flow_test_003",
        customer_id=None,
    )

    service.transition(
        call_id="flow_test_003",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_003",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="flow_test_003",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    result = service.authenticate(
        call_id="flow_test_003",
        machine=machine,
    )

    assert result.authenticated is True
    assert machine.current_state == CallState.DISCLOSE_OVERDUE
    assert result.current_state == "DISCLOSE_OVERDUE"
def test_handle_payment_action_records_disposition(
    db_session,
):
    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id="flow_test_004",
        customer_id=None,
    )

    service.transition(
        call_id="flow_test_004",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_004",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="flow_test_004",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    service.transition(
        call_id="flow_test_004",
        machine=machine,
        next_state=CallState.DISCLOSE_OVERDUE,
    )

    service.transition(
        call_id="flow_test_004",
        machine=machine,
        next_state=CallState.INTENT_HANDLING,
    )

    result = service.handle_action(
        call_id="flow_test_004",
        machine=machine,
        action=IntentAction.PAYMENT,
    )

    assert result.value == "PAYMENT_INITIATED"
    assert machine.current_state == CallState.DISPOSITION
def test_end_call_updates_state_and_call_log(
    db_session,
):
    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id="flow_test_005",
        customer_id=None,
    )

    service.transition(
        call_id="flow_test_005",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_005",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="flow_test_005",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    service.transition(
        call_id="flow_test_005",
        machine=machine,
        next_state=CallState.DISCLOSE_OVERDUE,
    )

    service.transition(
        call_id="flow_test_005",
        machine=machine,
        next_state=CallState.INTENT_HANDLING,
    )

    service.transition(
        call_id="flow_test_005",
        machine=machine,
        next_state=CallState.DISPOSITION,
    )

    result = service.end_call(
        call_id="flow_test_005",
        machine=machine,
    )

    assert machine.current_state == CallState.END
    assert result.ended_at is not None
def test_invalid_transition_does_not_update_session(
    db_session,
):
    service = create_service(db_session)

    machine, session, _ = service.start_call(
        call_id="flow_test_006",
        customer_id=None,
    )

    with pytest.raises(InvalidStateTransition):
        service.transition(
            call_id="flow_test_006",
            machine=machine,
            next_state=CallState.DISPOSITION,
        )

    assert machine.current_state == CallState.CALL_CONNECTED
    assert session.current_state == "CALL_CONNECTED"

def test_authentication_failure_ends_call(
    db_session,
):
    service = create_service(db_session)

    machine, session, _ = service.start_call(
        call_id="flow_test_008",
        customer_id=None,
    )

    service.transition(
        call_id="flow_test_008",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_008",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="flow_test_008",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    result = service.authentication_failed(
        call_id="flow_test_008",
        machine=machine,
    )

    assert machine.current_state == CallState.END
    assert result.current_state == "END"
    assert result.authenticated is False

def test_person_not_verified_ends_call(
    db_session,
):
    service = create_service(db_session)

    machine, session, _ = service.start_call(
        call_id="flow_test_009",
        customer_id=None,
    )

    service.transition(
        call_id="flow_test_009",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_009",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    result = service.person_not_verified(
        call_id="flow_test_009",
        machine=machine,
    )

    assert machine.current_state == CallState.END
    assert result.current_state == "END"
    assert result.authenticated is False


def test_complete_successful_payment_call_flow(
    db_session,
):
    service = create_service(db_session)

    machine, session, call_log = service.start_call(
        call_id="flow_test_010",
        customer_id=None,
    )

    assert machine.current_state == CallState.CALL_CONNECTED

    service.transition(
        call_id="flow_test_010",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_010",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="flow_test_010",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    authenticated_session = service.authenticate(
        call_id="flow_test_010",
        machine=machine,
    )

    assert authenticated_session.authenticated is True
    assert machine.current_state == CallState.DISCLOSE_OVERDUE

    service.transition(
        call_id="flow_test_010",
        machine=machine,
        next_state=CallState.INTENT_HANDLING,
    )

    disposition = service.handle_action(
        call_id="flow_test_010",
        machine=machine,
        action=IntentAction.PAYMENT,
    )

    assert disposition.value == "PAYMENT_INITIATED"
    assert machine.current_state == CallState.DISPOSITION

    ended_log = service.end_call(
        call_id="flow_test_010",
        machine=machine,
    )

    assert machine.current_state == CallState.END
    assert ended_log.call_id == "flow_test_010"
    assert ended_log.disposition == "PAYMENT_INITIATED"
    assert ended_log.ended_at is not None

def test_complete_successful_payment_call_flow(
    db_session,
):
    service = create_service(db_session)

    machine, session, call_log = service.start_call(
        call_id="flow_test_010",
        customer_id=None,
    )

    assert machine.current_state == CallState.CALL_CONNECTED

    service.transition(
        call_id="flow_test_010",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_010",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="flow_test_010",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    authenticated_session = service.authenticate(
        call_id="flow_test_010",
        machine=machine,
    )

    assert authenticated_session.authenticated is True
    assert machine.current_state == CallState.DISCLOSE_OVERDUE

    service.transition(
        call_id="flow_test_010",
        machine=machine,
        next_state=CallState.INTENT_HANDLING,
    )

    disposition = service.handle_action(
        call_id="flow_test_010",
        machine=machine,
        action=IntentAction.PAYMENT,
    )

    assert disposition.value == "PAYMENT_INITIATED"
    assert machine.current_state == CallState.DISPOSITION

    ended_log = service.end_call(
        call_id="flow_test_010",
        machine=machine,
    )

    assert machine.current_state == CallState.END
    assert ended_log.call_id == "flow_test_010"
    assert ended_log.disposition == "PAYMENT_INITIATED"
    assert ended_log.ended_at is not None


def test_complete_successful_ptp_call_flow(
    db_session,
):
    service = create_service(db_session)

    customer = Customer(
        name="PTP Test Customer",
        phone="9400000011",
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    loan = Loan(
        customer_id=customer.id,
        loan_type="PERSONAL",
        overdue_amount=Decimal("15000.00"),
        days_past_due=30,
    )

    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    machine, _, _ = service.start_call(
        call_id="flow_test_011",
        customer_id=customer.id,
    )

    service.transition(
        call_id="flow_test_011",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_011",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="flow_test_011",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    result = service.authenticate(
        call_id="flow_test_011",
        machine=machine,
    )

    assert result.authenticated is True
    assert machine.current_state == CallState.DISCLOSE_OVERDUE

    service.transition(
        call_id="flow_test_011",
        machine=machine,
        next_state=CallState.INTENT_HANDLING,
    )

    promise_date = date.today() + timedelta(days=7)

    disposition = service.handle_action(
        call_id="flow_test_011",
        machine=machine,
        action=IntentAction.PROMISE_TO_PAY,
        customer_id=customer.id,
        loan_id=loan.id,
        amount=Decimal("5000.00"),
        promise_date=promise_date,
    )

    assert disposition.value == "PTP_COMMITTED"
    assert machine.current_state == CallState.DISPOSITION

    promises = PromiseToPayRepository(
        db_session
    ).get_by_customer_id(customer.id)

    assert len(promises) == 1
    assert promises[0].customer_id == customer.id
    assert promises[0].loan_id == loan.id
    assert promises[0].amount == Decimal("5000.00")
    assert promises[0].promise_date == promise_date
    assert promises[0].status == "PENDING"

    ended_log = service.end_call(
        call_id="flow_test_011",
        machine=machine,
    )

    assert machine.current_state == CallState.END
    assert ended_log.call_id == "flow_test_011"
    assert ended_log.disposition == "PTP_COMMITTED"
    assert ended_log.ended_at is not None

def test_complete_successful_dispute_call_flow(
    db_session,
):
    service = create_service(db_session)

    customer = Customer(
        name="Dispute Test Customer",
        phone="9400000012",
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    machine, _, _ = service.start_call(
        call_id="flow_test_012",
        customer_id=customer.id,
    )

    service.transition(
        call_id="flow_test_012",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_012",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="flow_test_012",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    result = service.authenticate(
        call_id="flow_test_012",
        machine=machine,
    )

    assert result.authenticated is True
    assert machine.current_state == CallState.DISCLOSE_OVERDUE

    service.transition(
        call_id="flow_test_012",
        machine=machine,
        next_state=CallState.INTENT_HANDLING,
    )

    disposition = service.handle_action(
        call_id="flow_test_012",
        machine=machine,
        action=IntentAction.DISPUTE,
        customer_id=customer.id,
    )

    assert disposition.value == "DISPUTE_RAISED"
    assert machine.current_state == CallState.DISPOSITION

    ended_log = service.end_call(
        call_id="flow_test_012",
        machine=machine,
    )

    assert machine.current_state == CallState.END
    assert ended_log.call_id == "flow_test_012"
    assert ended_log.disposition == "DISPUTE_RAISED"
    assert ended_log.ended_at is not None

def test_complete_successful_assistance_call_flow(
    db_session,
):
    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id="flow_test_013",
        customer_id=None,
    )

    service.transition(
        call_id="flow_test_013",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_013",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="flow_test_013",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    result = service.authenticate(
        call_id="flow_test_013",
        machine=machine,
    )

    assert result.authenticated is True
    assert machine.current_state == CallState.DISCLOSE_OVERDUE

    service.transition(
        call_id="flow_test_013",
        machine=machine,
        next_state=CallState.INTENT_HANDLING,
    )

    disposition = service.handle_action(
        call_id="flow_test_013",
        machine=machine,
        action=IntentAction.ASSISTANCE,
    )

    assert disposition.value == "NEGOTIATION_REQUIRED"
    assert machine.current_state == CallState.DISPOSITION

    ended_log = service.end_call(
        call_id="flow_test_013",
        machine=machine,
    )

    assert machine.current_state == CallState.END
    assert ended_log.call_id == "flow_test_013"
    assert ended_log.disposition == "NEGOTIATION_REQUIRED"
    assert ended_log.ended_at is not None

def test_complete_successful_clarification_call_flow(
    db_session,
):
    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id="flow_test_014",
        customer_id=None,
    )

    service.transition(
        call_id="flow_test_014",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_014",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="flow_test_014",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    result = service.authenticate(
        call_id="flow_test_014",
        machine=machine,
    )

    assert result.authenticated is True
    assert machine.current_state == CallState.DISCLOSE_OVERDUE

    service.transition(
        call_id="flow_test_014",
        machine=machine,
        next_state=CallState.INTENT_HANDLING,
    )

    disposition = service.handle_action(
        call_id="flow_test_014",
        machine=machine,
        action=IntentAction.CLARIFICATION,
    )

    assert disposition.value == "CLARIFICATION_REQUIRED"
    assert machine.current_state == CallState.DISPOSITION

    ended_log = service.end_call(
        call_id="flow_test_014",
        machine=machine,
    )

    assert machine.current_state == CallState.END
    assert ended_log.call_id == "flow_test_014"
    assert ended_log.disposition == "CLARIFICATION_REQUIRED"
    assert ended_log.ended_at is not None



def test_ptp_transaction_rolls_back_on_failure(
    db_session,
    monkeypatch,
):
    service = create_service(db_session)

    customer = Customer(
        name="Rollback Test Customer",
        phone="9400000099",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    loan = Loan(
        customer_id=customer.id,
        loan_type="PERSONAL",
        overdue_amount=Decimal("15000.00"),
        days_past_due=30,
    )
    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    machine, session, _ = service.start_call(
        call_id="flow_test_rollback_001",
        customer_id=customer.id,
    )

    service.transition(
        call_id="flow_test_rollback_001",
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    service.transition(
        call_id="flow_test_rollback_001",
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    service.transition(
        call_id="flow_test_rollback_001",
        machine=machine,
        next_state=CallState.AUTHENTICATION,
    )

    service.authenticate(
        call_id="flow_test_rollback_001",
        machine=machine,
    )

    service.transition(
        call_id="flow_test_rollback_001",
        machine=machine,
        next_state=CallState.INTENT_HANDLING,
    )

    def fail_transition(*args, **kwargs):
        raise RuntimeError("forced transaction failure")

    monkeypatch.setattr(
        service,
        "transition",
        fail_transition,
    )

    promise_date = date.today() + timedelta(days=7)

    with pytest.raises(RuntimeError, match="forced transaction failure"):
        service.handle_action(
            call_id="flow_test_rollback_001",
            machine=machine,
            action=IntentAction.PROMISE_TO_PAY,
            customer_id=customer.id,
            loan_id=loan.id,
            amount=Decimal("5000.00"),
            promise_date=promise_date,
        )

    db_session.expire_all()

    promises = PromiseToPayRepository(
        db_session
    ).get_by_customer_id(customer.id)

    assert promises == []

    refreshed_session = SessionRepository(
        db_session
    ).get_by_call_id("flow_test_rollback_001")

    assert refreshed_session.current_state == "INTENT_HANDLING"

    assert machine.current_state == CallState.INTENT_HANDLING







