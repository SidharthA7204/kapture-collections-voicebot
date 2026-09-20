from datetime import datetime

from app.db.repositories.customer_repository import (
    CustomerRepository,
)
from app.models.customer import Customer
from app.services.customer_service import (
    CustomerService,
)


def create_customer(db_session):
    customer = Customer(
        name="Security Test Customer",
        phone="9876543210",
        dob=datetime(
            1995,
            5,
            15,
        ),
    )

    return CustomerRepository(
        db_session
    ).create(customer)


def test_three_failed_verifications_end_call(
    db_session,
):
    from tests.test_call_termination_consistency import (
        create_service,
        move_to_authentication,
    )

    customer = create_customer(
        db_session
    )

    service = create_service(
        db_session
    )

    call_id = "security_attempts_001"

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=customer.id,
    )

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    for attempt in range(3):
        result = service.verify_customer(
            call_id=call_id,
            machine=machine,
            phone="9999999999",
            dob=datetime(
                1995,
                5,
                15,
            ).date(),
        )

        if attempt < 2:
            assert result["current_state"] == (
                "AUTHENTICATION"
            )
            assert result["authenticated"] is False

    assert result["current_state"] == "END"
    assert result["authenticated"] is False
