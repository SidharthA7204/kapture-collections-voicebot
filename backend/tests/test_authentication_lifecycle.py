from datetime import datetime

from fastapi.testclient import TestClient

from app.db.database import get_db
from app.db.repositories.customer_repository import (
    CustomerRepository,
)
from app.main import app
from app.models.customer import Customer


def create_customer(db_session):
    customer = Customer(
        name="Lifecycle Customer",
        phone="9876543210",
        dob=datetime(1995, 5, 15),
    )

    return CustomerRepository(db_session).create(
        customer
    )


def move_to_authentication(
    client,
    call_id,
):
    for state in (
        "INTRODUCTION",
        "CHECK_PERSON",
        "AUTHENTICATION",
    ):
        response = client.post(
            f"/calls/{call_id}/transition",
            json={
                "next_state": state,
            },
        )

        assert response.status_code == 200
        assert (
            response.json()["current_state"]
            == state
        )


def test_full_authentication_lifecycle_success(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        customer = create_customer(db_session)

        call_id = "lifecycle_success_001"

        response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer.id,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["call_id"] == call_id
        assert data["authenticated"] is False
        assert data["current_state"] == "CALL_CONNECTED"

        move_to_authentication(
            client,
            call_id,
        )

        response = client.post(
            f"/calls/{call_id}/verify-customer",
            json={
                "phone": "9876543210",
                "dob": "1995-05-15",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["call_id"] == call_id
        assert data["authenticated"] is True
        assert data["current_state"] == "DISCLOSE_OVERDUE"

    finally:
        app.dependency_overrides.clear()


def test_full_authentication_lifecycle_failure(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        customer = create_customer(db_session)

        call_id = "lifecycle_failure_001"

        response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer.id,
            },
        )

        assert response.status_code == 200

        move_to_authentication(
            client,
            call_id,
        )

        for attempt in range(1, 4):
            response = client.post(
                f"/calls/{call_id}/verify-customer",
                json={
                    "phone": "9999999999",
                    "dob": "1995-05-15",
                },
            )

            assert response.status_code == 200

            data = response.json()

            assert data["call_id"] == call_id
            assert data["authenticated"] is False

            if attempt < 3:
                assert (
                    data["current_state"]
                    == "AUTHENTICATION"
                )
            else:
                assert (
                    data["current_state"]
                    == "END"
                )

    finally:
        app.dependency_overrides.clear()