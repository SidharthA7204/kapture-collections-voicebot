from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_call_event_service,
)
from app.routes.calls import router


class FakeCallEventService:

    def get_call_events(self, call_id: str):
        return []


def create_test_app():
    app = FastAPI()

    app.include_router(router)

    app.dependency_overrides[
        get_call_event_service
    ] = lambda: FakeCallEventService()

    return app


def test_call_id_cannot_be_excessively_long():
    app = create_test_app()
    client = TestClient(app)

    call_id = "a" * 300

    response = client.get(
        f"/calls/{call_id}/events"
    )

    assert response.status_code == 422


def test_call_id_cannot_be_empty():
    app = create_test_app()
    client = TestClient(app)

    response = client.get(
        "/calls//events"
    )

    assert response.status_code == 404


def test_normal_call_id_is_accepted():
    app = create_test_app()
    client = TestClient(app)

    response = client.get(
        "/calls/security-test-001/events"
    )

    assert response.status_code == 200

    assert response.json() == {
        "call_id": "security-test-001",
        "events": [],
    }
