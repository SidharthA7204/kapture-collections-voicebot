import pytest
from datetime import date
from decimal import Decimal
from app.models.promise_to_pay import PromiseToPay
from app.state.states import CallState
from app.state.state_machine import (
    CallStateMachine,
    InvalidStateTransition,
)


def test_valid_call_flow():

    machine = CallStateMachine()

    machine.transition(CallState.INTRODUCTION)
    machine.transition(CallState.CHECK_PERSON)
    machine.transition(CallState.AUTHENTICATION)
    machine.transition(CallState.DISCLOSE_OVERDUE)
    machine.transition(CallState.INTENT_HANDLING)
    machine.transition(CallState.DISPOSITION)
    machine.transition(CallState.END)

    assert machine.current_state == CallState.END
    
def test_promise_to_pay_model():

    ptp = PromiseToPay(
        customer_id=1,
        loan_id=1,
        amount=Decimal("5000.00"),
        promise_date=date(2026, 8, 20),
        status="PENDING",
    )

    assert ptp.customer_id == 1
    assert ptp.loan_id == 1
    assert ptp.amount == Decimal("5000.00")
    assert ptp.promise_date == date(2026, 8, 20)
    assert ptp.status == "PENDING"


def test_invalid_state_transition():

    machine = CallStateMachine()

    with pytest.raises(InvalidStateTransition):
        machine.transition(CallState.DISPOSITION)