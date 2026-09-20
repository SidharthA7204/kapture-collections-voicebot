from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def valid_payload(call_id="vapi-call-001"):
    return {
        "message": {
            "type": "status-update",
            "call": {
                "id": call_id,
                "status": "in-progress",
            },
        }
    }


def valid_headers():
    return {
        "Authorization": (
            f"Bearer {settings.VAPI_WEBHOOK_SECRET}"
        )
    }


def test_vapi_webhook_creates_call_session():
    client = TestClient(app)

    response = client.post(
        "/vapi/webhook",
        json=valid_payload(
            "vapi-new-call-001"
        ),
        headers=valid_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["event_type"] == "status-update"
    assert data["call_id"] == "vapi-new-call-001"


def test_vapi_webhook_is_idempotent():
    client = TestClient(app)

    payload = valid_payload(
        "vapi-idempotent-001"
    )

    first = client.post(
        "/vapi/webhook",
        json=payload,
        headers=valid_headers(),
    )

    second = client.post(
        "/vapi/webhook",
        json=payload,
        headers=valid_headers(),
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.json()["call_id"] == (
        "vapi-idempotent-001"
    )

    assert second.json()["call_id"] == (
        "vapi-idempotent-001"
    )
