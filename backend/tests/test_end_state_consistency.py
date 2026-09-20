import pytest

from app.state.state_machine import InvalidStateTransition
from app.state.states import CallState


def test_end_state_cannot_transition_to_active_state(
    db_session,
):
    from tests.test_call_termination_consistency import (
        create_service,
        move_to_authentication,
    )

    service = create_service(db_session)

    call_id = "end_state_001"

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    service.end_call(
        call_id=call_id,
        machine=machine,
    )

    assert machine.current_state == CallState.END

    with pytest.raises(InvalidStateTransition):
        service.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.AUTHENTICATION,
        )

def test_end_state_cannot_be_verified(
    db_session,
):
    from tests.test_call_termination_consistency import (
        create_customer,
        create_service,
        move_to_authentication,
    )

    customer = create_customer(db_session)
    service = create_service(db_session)

    call_id = "end_state_002"

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=customer.id,
    )

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    service.end_call(
        call_id=call_id,
        machine=machine,
    )

    assert machine.current_state == CallState.END

    with pytest.raises(InvalidStateTransition):
        service.verify_customer(
            call_id=call_id,
            machine=machine,
            phone="9876543210",
            dob=__import__("datetime").date(
                1995,
                5,
                15,
            ),
        )