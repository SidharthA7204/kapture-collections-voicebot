from datetime import datetime

from fastapi.testclient import TestClient

from app.db.repositories.customer_repository import (
    CustomerRepository,
)
from app.db.database import get_db
from app.main import app
from app.models.customer import Customer


def create_customer(db_session):
    customer = Customer(
        name="API Verification Customer",
        phone="9876543210",
        dob=datetime(1995, 5, 15),
    )

    return CustomerRepository(db_session).create(
        customer
    )


def move_call_to_authentication(
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


def test_customer_verification_endpoint_success(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        customer = create_customer(db_session)

        call_id = "api_verification_001"

        response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer.id,
            },
        )

        assert response.status_code == 200

        move_call_to_authentication(
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
        assert (
            data["current_state"]
            == "DISCLOSE_OVERDUE"
        )

    finally:
        app.dependency_overrides.clear()


def test_customer_verification_endpoint_wrong_phone(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        customer = create_customer(db_session)

        call_id = "api_verification_002"

        response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer.id,
            },
        )

        assert response.status_code == 200

        move_call_to_authentication(
            client,
            call_id,
        )

        response = client.post(
            f"/calls/{call_id}/verify-customer",
            json={
                "phone": "9999999999",
                "dob": "1995-05-15",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["authenticated"] is False
        assert (
            data["current_state"]
            == "AUTHENTICATION"
        )

    finally:
        app.dependency_overrides.clear()

def test_customer_verification_endpoint_third_failure_ends_call(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        customer = create_customer(db_session)

        call_id = "api_verification_003"

        response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer.id,
            },
        )

        assert response.status_code == 200

        move_call_to_authentication(
            client,
            call_id,
        )

        # First failed attempt
        response = client.post(
            f"/calls/{call_id}/verify-customer",
            json={
                "phone": "9999999999",
                "dob": "1995-05-15",
            },
        )

        assert response.status_code == 200
        assert (
            response.json()["authenticated"]
            is False
        )
        assert (
            response.json()["current_state"]
            == "AUTHENTICATION"
        )

        # Second failed attempt
        response = client.post(
            f"/calls/{call_id}/verify-customer",
            json={
                "phone": "9999999999",
                "dob": "1995-05-15",
            },
        )

        assert response.status_code == 200
        assert (
            response.json()["authenticated"]
            is False
        )
        assert (
            response.json()["current_state"]
            == "AUTHENTICATION"
        )

        # Third failed attempt
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
        assert data["current_state"] == "END"

    finally:
        app.dependency_overrides.clear()