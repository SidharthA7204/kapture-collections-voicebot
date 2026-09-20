from fastapi.testclient import TestClient

from app.db.database import get_db
from app.main import app


def test_transition_endpoint_persists_state(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        start_response = client.post(
            "/calls/start",
            json={
                "call_id": "transition_api_001",
                "customer_id": None,
            },
        )

        assert start_response.status_code == 200

        start_data = start_response.json()

        assert start_data["current_state"] == "CALL_CONNECTED"

        introduction_response = client.post(
            "/calls/transition_api_001/transition",
            json={
                "next_state": "INTRODUCTION",
            },
        )

        assert introduction_response.status_code == 200

        introduction_data = (
            introduction_response.json()
        )

        assert (
            introduction_data["call_id"]
            == "transition_api_001"
        )

        assert (
            introduction_data["current_state"]
            == "INTRODUCTION"
        )

        check_person_response = client.post(
            "/calls/transition_api_001/transition",
            json={
                "next_state": "CHECK_PERSON",
            },
        )

        assert check_person_response.status_code == 200

        check_person_data = (
            check_person_response.json()
        )

        assert (
            check_person_data["current_state"]
            == "CHECK_PERSON"
        )

    finally:
        app.dependency_overrides.clear()