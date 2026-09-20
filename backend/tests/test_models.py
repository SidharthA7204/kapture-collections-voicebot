from decimal import Decimal
from app.models.dispute import Dispute
from app.models.customer import Customer
from app.models.loan import Loan
from app.models.session import Session
from datetime import datetime
from app.models.call_log import CallLog
from app.models.dispute import Dispute
def test_customer_model():

    customer = Customer(
        name="Test Customer",
        phone="9999999999",
    )

    assert customer.name == "Test Customer"
    assert customer.phone == "9999999999"


def test_loan_model():

    loan = Loan(
        customer_id=1,
        loan_type="PERSONAL",
        overdue_amount=Decimal("12500.00"),
        days_past_due=30,
    )

    assert loan.customer_id == 1
    assert loan.loan_type == "PERSONAL"
    assert loan.overdue_amount == Decimal("12500.00")
    assert loan.days_past_due == 30
def test_session_model():

    session = Session(
        call_id="call_test_001",
        customer_id=1,
        authenticated=False,
        current_state="CALL_CONNECTED",
    )

    assert session.call_id == "call_test_001"
    assert session.customer_id == 1
    assert session.authenticated is False
    assert session.current_state == "CALL_CONNECTED"

def test_call_log_model():

    started_at = datetime(2026, 8, 14, 10, 0, 0)

    call_log = CallLog(
        call_id="call_test_001",
        customer_id=1,
        disposition="PTP_COMMITTED",
        transcript_ref="transcripts/call_test_001.json",
        started_at=started_at,
    )

    assert call_log.call_id == "call_test_001"
    assert call_log.customer_id == 1
    assert call_log.disposition == "PTP_COMMITTED"
    assert call_log.transcript_ref == "transcripts/call_test_001.json"
    assert call_log.started_at == started_at

def test_dispute_model():

    dispute = Dispute(
        customer_id=1,
        loan_id=1,
        reason="INCORRECT_AMOUNT",
        description="Customer says the overdue amount is incorrect.",
        status="OPEN",
    )

    assert dispute.customer_id == 1
    assert dispute.loan_id == 1
    assert dispute.reason == "INCORRECT_AMOUNT"
    assert dispute.status == "OPEN"