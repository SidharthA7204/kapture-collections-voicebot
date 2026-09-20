from fastapi.testclient import TestClient

from app.db.database import get_db
from app.models.customer import Customer
from app.main import app


def test_start_call_endpoint(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/calls/start",
            json={
                "call_id": "api_test_001",
                "customer_id": None,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["call_id"] == "api_test_001"
        assert data["customer_id"] is None
        assert data["current_state"] == "CALL_CONNECTED"
        assert data["authenticated"] is False

    finally:
        app.dependency_overrides.clear()


def test_transition_unknown_call_returns_404():
    client = TestClient(app)

    response = client.post(
        "/calls/nonexistent-call-001/transition",
        json={
            "next_state": "INTRODUCTION",
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "error": "NOT_FOUND",
        "detail": (
            "Session not found: nonexistent-call-001"
        ),
    }


def test_start_call_rejects_different_customer_for_existing_call(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer_one = Customer(
            name="Customer One",
            phone="9000000001",
        )

        customer_two = Customer(
            name="Customer Two",
            phone="9000000002",
        )

        db_session.add_all(
            [
                customer_one,
                customer_two,
            ]
        )
        db_session.commit()

        db_session.refresh(customer_one)
        db_session.refresh(customer_two)

        client = TestClient(app)

        call_id = "customer-consistency-001"

        first = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer_one.id,
            },
        )

        assert first.status_code == 200

        second = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer_two.id,
            },
        )

        assert second.status_code == 409

    finally:
        app.dependency_overrides.clear()
