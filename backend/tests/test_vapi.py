from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings


client = TestClient(app)


def test_vapi_webhook_rejects_invalid_authorization():
    response = client.post(
        "/vapi/webhook",
        headers={
            "Authorization": "Bearer wrong-secret",
        },
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "id": "call-test-001",
                    "status": "in-progress",
                },
            }
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


def test_vapi_webhook_accepts_valid_authorization(monkeypatch):
    service = Mock()

    session = Mock()
    session.call_id = "call-test-002"

    service.handle_status_update.return_value = session

    from app.api.dependencies import get_vapi_webhook_service

    app.dependency_overrides[
        get_vapi_webhook_service
    ] = lambda: service

    try:
        response = client.post(
            "/vapi/webhook",
            headers={
                "Authorization": (
                    f"Bearer {settings.VAPI_WEBHOOK_SECRET}"
                ),
            },
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": "call-test-002",
                        "status": "in-progress",
                    },
                }
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "ok"
        assert data["event_type"] == "status-update"
        assert data["call_id"] == "call-test-002"

        service.handle_status_update.assert_called_once_with(
            call_id="call-test-002",
            status="in-progress",
        )

    finally:
        app.dependency_overrides.pop(
            get_vapi_webhook_service,
            None,
        )


def test_vapi_webhook_handles_non_status_event(monkeypatch):
    service = Mock()

    from app.api.dependencies import get_vapi_webhook_service

    app.dependency_overrides[
        get_vapi_webhook_service
    ] = lambda: service

    try:
        response = client.post(
            "/vapi/webhook",
            headers={
                "Authorization": (
                    f"Bearer {settings.VAPI_WEBHOOK_SECRET}"
                ),
            },
            json={
                "message": {
                    "type": "conversation-update",
                    "call": {
                        "id": "call-test-003",
                        "status": "in-progress",
                    },
                }
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "ok"
        assert data["event_type"] == "conversation-update"
        assert data["call_id"] == "call-test-003"

        service.handle_status_update.assert_not_called()

    finally:
        app.dependency_overrides.pop(
            get_vapi_webhook_service,
            None,
        )


def test_vapi_webhook_requires_call_information():
    response = client.post(
        "/vapi/webhook",
        headers={
            "Authorization": (
                f"Bearer {settings.VAPI_WEBHOOK_SECRET}"
            ),
        },
        json={
            "message": {
                "type": "status-update",
                "call": None,
            }
        },
    )

    assert response.status_code in (422,)


def test_vapi_webhook_rejects_missing_authorization():
    response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "id": "call-test-005",
                    "status": "in-progress",
                },
            }
        },
    )

    assert response.status_code == 401
