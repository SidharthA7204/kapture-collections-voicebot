from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import settings
from app.db.database import SessionLocal
from app.main import app
from app.models.session import Session
from app.state.states import CallState


def test_vapi_late_in_progress_does_not_resurrect_ended_call():
    client = TestClient(app)

    call_id = "vapi-late-progress-001"

    headers = {
        "Authorization": (
            f"Bearer {settings.VAPI_WEBHOOK_SECRET}"
        )
    }

    ended_response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "id": call_id,
                    "status": "ended",
                },
            }
        },
        headers=headers,
    )

    assert ended_response.status_code == 200

    late_response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "id": call_id,
                    "status": "in-progress",
                },
            }
        },
        headers=headers,
    )

    assert late_response.status_code == 200
    assert late_response.json()["call_id"] == call_id

    with SessionLocal() as db:
        session = db.scalar(
            select(Session).where(
                Session.call_id == call_id
            )
        )

        assert session is not None
        assert session.current_state == CallState.END.value
from sqlalchemy import select

from app.models.call_log import CallLog


def test_vapi_late_in_progress_does_not_reopen_call_log():
    call_id = "vapi-late-log-001"

    client = TestClient(app)

    headers = {
        "Authorization": (
            f"Bearer {settings.VAPI_WEBHOOK_SECRET}"
        )
    }

    ended_response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "id": call_id,
                    "status": "ended",
                },
            }
        },
        headers=headers,
    )

    assert ended_response.status_code == 200

    with SessionLocal() as db:
        call_log = db.scalar(
            select(CallLog).where(
                CallLog.call_id == call_id
            )
        )

        assert call_log is not None
        assert call_log.ended_at is not None

        ended_at = call_log.ended_at

    late_response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "id": call_id,
                    "status": "in-progress",
                },
            }
        },
        headers=headers,
    )

    assert late_response.status_code == 200

    with SessionLocal() as db:
        call_log = db.scalar(
            select(CallLog).where(
                CallLog.call_id == call_id
            )
        )

        assert call_log is not None
        assert call_log.ended_at is not None
        assert call_log.ended_at == ended_at
from sqlalchemy import func, select

from app.models.call_event import CallEvent


def test_vapi_repeated_ended_does_not_duplicate_call_ended_event():
    call_id = "vapi-ended-event-once-001"

    client = TestClient(app)

    headers = {
        "Authorization": (
            f"Bearer {settings.VAPI_WEBHOOK_SECRET}"
        )
    }

    payload = {
        "message": {
            "type": "status-update",
            "call": {
                "id": call_id,
                "status": "ended",
            },
        }
    }

    first = client.post(
        "/vapi/webhook",
        json=payload,
        headers=headers,
    )

    assert first.status_code == 200

    second = client.post(
        "/vapi/webhook",
        json=payload,
        headers=headers,
    )

    assert second.status_code == 200

    with SessionLocal() as db:
        count = db.scalar(
            select(func.count())
            .select_from(CallEvent)
            .where(
                CallEvent.call_id == call_id,
                CallEvent.event_type == "CALL_ENDED",
            )
        )

        assert count == 1
