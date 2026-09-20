from app.db.repositories.dispute_repository import DisputeRepository
from app.db.repositories.promise_to_pay_repository import (
    PromiseToPayRepository,
)
from app.schemas.payment import PaymentStatus
from app.services.payment_service import PaymentService
from app.models.customer import Customer
from app.models.loan import Loan
from app.schemas.intent import CustomerIntent
from app.schemas.intent_action import IntentAction
from app.services.collections_intent_service import (
    CollectionsIntentService,
)
from app.services.disposition_service import DispositionService
from app.services.assistance_service import AssistanceService
from app.services.dispute_service import DisputeService
from app.services.intent_service import IntentService
from app.services.promise_to_pay_service import PromiseToPayService
from datetime import date, timedelta
from app.schemas.assistance import AssistanceOutcome
from decimal import Decimal
from app.db.repositories.call_log_repository import (
    CallLogRepository,
)
from app.services.call_log_service import CallLogService
def create_service(db_session):
    intent_service = IntentService()
    payment_service = PaymentService()
    dispute_repository = DisputeRepository(db_session)
    dispute_service = DisputeService(dispute_repository)
    assistance_service = AssistanceService()
    ptp_repository = PromiseToPayRepository(db_session)
    ptp_service = PromiseToPayService(ptp_repository)
    disposition_service = DispositionService()
    call_log_repository = CallLogRepository(db_session)
    call_log_service = CallLogService(call_log_repository)

    return CollectionsIntentService(
        intent_service=intent_service,
        dispute_service=dispute_service,
        promise_to_pay_service=ptp_service,
        payment_service=payment_service,
        assistance_service=assistance_service,
        disposition_service=disposition_service,
        call_log_service=call_log_service,
    )

def test_collections_intent_service_can_be_created(db_session):
    service = create_service(db_session)

    assert service is not None


def test_dispute_intent_maps_to_dispute_action(db_session):
    service = create_service(db_session)

    action = service.determine_action(
        CustomerIntent.DISPUTE
    )

    assert action == IntentAction.DISPUTE


def test_dispute_intent_can_create_dispute(
    db_session,
):
    service = create_service(db_session)

    customer = Customer(
        name="Integration Test Customer",
        phone="9700000001",
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    result = service.create_dispute(
        customer_id=customer.id,
        loan_id=None,
        reason="incorrect_amount",
        description="Customer disputes the overdue amount.",
    )

    assert result.id is not None
    assert result.customer_id == customer.id
    assert result.loan_id is None
    assert result.reason == "INCORRECT_AMOUNT"
    assert result.status == "OPEN"
def test_promise_to_pay_intent_maps_to_ptp_action(
    db_session,
):
    service = create_service(db_session)

    action = service.determine_action(
        CustomerIntent.PROMISE_TO_PAY
    )

    assert action == IntentAction.PROMISE_TO_PAY
def test_promise_to_pay_intent_can_create_promise(
    db_session,
):
    service = create_service(db_session)

    customer = Customer(
        name="PTP Integration Customer",
        phone="9700000002",
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    loan = Loan(
        customer_id=customer.id,
        loan_type="PERSONAL",
        overdue_amount=Decimal("10000.00"),
        days_past_due=30,
    )

    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    promise_date = date.today() + timedelta(days=5)

    result = service.create_promise(
        customer_id=customer.id,
        loan_id=loan.id,
        amount=Decimal("5000.00"),
        promise_date=promise_date,
    )

    assert result.id is not None
    assert result.customer_id == customer.id
    assert result.loan_id == loan.id
    assert result.amount == Decimal("5000.00")
    assert result.promise_date == promise_date
    assert result.status == "PENDING"
def test_pay_now_intent_maps_to_payment_action(
    db_session,
):
    service = create_service(db_session)

    action = service.determine_action(
        CustomerIntent.PAY_NOW
    )

    assert action == IntentAction.PAYMENT
def test_pay_now_intent_can_initiate_payment(
    db_session,
):
    service = create_service(db_session)

    result = service.initiate_payment(
        customer_id=1,
        loan_id=1,
        amount=Decimal("5000.00"),
    )

    assert result == PaymentStatus.INITIATED

def test_unable_to_pay_intent_maps_to_assistance_action(
    db_session,
):
    service = create_service(db_session)

    action = service.determine_action(
        CustomerIntent.UNABLE_TO_PAY
    )

    assert action == IntentAction.ASSISTANCE


def test_unable_to_pay_intent_requires_negotiation(
    db_session,
):
    service = create_service(db_session)

    result = service.handle_unable_to_pay(
        customer_id=1,
        loan_id=1,
    )

    assert result == AssistanceOutcome.NEGOTIATION_REQUIRED

def test_payment_action_can_determine_disposition(
    db_session,
):
    service = create_service(db_session)

    result = service.determine_disposition(
        IntentAction.PAYMENT
    )

    assert result.value == "PAYMENT_INITIATED"


def test_ptp_action_can_determine_disposition(
    db_session,
):
    service = create_service(db_session)

    result = service.determine_disposition(
        IntentAction.PROMISE_TO_PAY
    )

    assert result.value == "PTP_COMMITTED"


def test_dispute_action_can_determine_disposition(
    db_session,
):
    service = create_service(db_session)

    result = service.determine_disposition(
        IntentAction.DISPUTE
    )

    assert result.value == "DISPUTE_RAISED"


def test_assistance_action_can_determine_disposition(
    db_session,
):
    service = create_service(db_session)

    result = service.determine_disposition(
        IntentAction.ASSISTANCE
    )

    assert result.value == "NEGOTIATION_REQUIRED"


def test_clarification_action_can_determine_disposition(
    db_session,
):
    service = create_service(db_session)

    result = service.determine_disposition(
        IntentAction.CLARIFICATION
    )

    assert result.value == "CLARIFICATION_REQUIRED"

def test_payment_action_can_record_call_disposition(
    db_session,
):
    service = create_service(db_session)

    service.call_log_service.start_call(
        call_id="integration_call_001",
        customer_id=None,
    )

    result = service.record_call_disposition(
        call_id="integration_call_001",
        action=IntentAction.PAYMENT,
    )

    assert result.call_id == "integration_call_001"
    assert result.disposition == "PAYMENT_INITIATED"

def test_ptp_action_can_record_call_disposition(
    db_session,
):
    service = create_service(db_session)

    service.call_log_service.start_call(
        call_id="integration_call_002",
        customer_id=None,
    )

    result = service.record_call_disposition(
        call_id="integration_call_002",
        action=IntentAction.PROMISE_TO_PAY,
    )

    assert result.disposition == "PTP_COMMITTED"


def test_dispute_action_can_record_call_disposition(
    db_session,
):
    service = create_service(db_session)

    service.call_log_service.start_call(
        call_id="integration_call_003",
        customer_id=None,
    )

    result = service.record_call_disposition(
        call_id="integration_call_003",
        action=IntentAction.DISPUTE,
    )

    assert result.disposition == "DISPUTE_RAISED"


def test_assistance_action_can_record_call_disposition(
    db_session,
):
    service = create_service(db_session)

    service.call_log_service.start_call(
        call_id="integration_call_004",
        customer_id=None,
    )

    result = service.record_call_disposition(
        call_id="integration_call_004",
        action=IntentAction.ASSISTANCE,
    )

    assert result.disposition == "NEGOTIATION_REQUIRED"


def test_clarification_action_can_record_call_disposition(
    db_session,
):
    service = create_service(db_session)

    service.call_log_service.start_call(
        call_id="integration_call_005",
        customer_id=None,
    )

    result = service.record_call_disposition(
        call_id="integration_call_005",
        action=IntentAction.CLARIFICATION,
    )

    assert result.disposition == "CLARIFICATION_REQUIRED"