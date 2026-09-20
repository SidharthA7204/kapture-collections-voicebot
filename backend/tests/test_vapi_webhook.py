from fastapi.testclient import TestClient

from app.main import app


def valid_headers():
    from app.core.config import settings

    return {
        "Authorization": (
            f"Bearer {settings.VAPI_WEBHOOK_SECRET}"
        )
    }


def test_vapi_ended_status_terminates_existing_active_call(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.call_event_repository import (
        CallEventRepository,
    )
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from app.state.states import CallState

    from tests.test_call_flow_service import (
        create_service,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-state-sync-003"

        service = create_service(db_session)

        machine, session, call_log = service.start_call(
            call_id=call_id,
            customer_id=None,
        )

        service.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.INTRODUCTION,
        )

        service.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.CHECK_PERSON,
        )

        service.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.AUTHENTICATION,
        )

        client = TestClient(app)

        response = client.post(
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
            headers=valid_headers(),
        )

        assert response.status_code == 200

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.current_state == (
            CallState.END.value
        )

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.ended_at is not None

        events = (
            CallEventRepository(db_session)
            .get_by_call_id(call_id)
        )

        ended_events = [
            event
            for event in events
            if event.event_type == "CALL_ENDED"
        ]

        assert len(ended_events) == 1

    finally:
        app.dependency_overrides.clear()
def test_vapi_webhook_rejects_missing_call_id():
    client = TestClient(app)

    response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "status": "in-progress",
                },
            },
        },
        headers=valid_headers(),
    )

    assert response.status_code == 422

def test_vapi_webhook_rejects_missing_message():
    client = TestClient(app)

    response = client.post(
        "/vapi/webhook",
        json={},
        headers=valid_headers(),
    )

    assert response.status_code == 422

def test_vapi_webhook_rejects_missing_call():
    client = TestClient(app)

    response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
            },
        },
        headers=valid_headers(),
    )

    assert response.status_code == 422

def test_vapi_webhook_rejects_missing_message_type():
    client = TestClient(app)

    response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "call": {
                    "id": "vapi-missing-type-001",
                    "status": "in-progress",
                },
            },
        },
        headers=valid_headers(),
    )

    assert response.status_code == 422

def test_vapi_webhook_accepts_missing_call_status():
    client = TestClient(app)

    response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "id": "vapi-missing-status-001",
                },
            },
        },
        headers=valid_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["event_type"] == "status-update"
    assert data["call_id"] == (
        "vapi-missing-status-001"
    )

def test_vapi_webhook_rejects_invalid_call_id_type():
    client = TestClient(app)

    response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "id": 12345,
                    "status": "in-progress",
                },
            },
        },
        headers=valid_headers(),
    )

    assert response.status_code == 422

def test_vapi_webhook_rejects_invalid_message_type():
    client = TestClient(app)

    response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": 12345,
                "call": {
                    "id": "vapi-invalid-type-001",
                    "status": "in-progress",
                },
            },
        },
        headers=valid_headers(),
    )

    assert response.status_code == 422

def test_vapi_webhook_rejects_invalid_call_status_type():
    client = TestClient(app)

    response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "id": "vapi-invalid-status-001",
                    "status": 12345,
                },
            },
        },
        headers=valid_headers(),
    )

    assert response.status_code == 422

def test_vapi_webhook_rejects_empty_call_id():
    client = TestClient(app)

    response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "id": "",
                    "status": "in-progress",
                },
            },
        },
        headers=valid_headers(),
    )

    assert response.status_code == 422

def test_vapi_webhook_rejects_empty_call_id():
    client = TestClient(app)

    response = client.post(
        "/vapi/webhook",
        json={
            "message": {
                "type": "status-update",
                "call": {
                    "id": "",
                    "status": "in-progress",
                },
            },
        },
        headers=valid_headers(),
    )

    assert response.status_code == 422

def test_vapi_in_progress_does_not_resurrect_ended_call(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from app.main import app
    from app.services.session_service import (
        SessionService,
    )
    from app.state.states import CallState

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-no-resurrection-001"

        session_service = SessionService(
            SessionRepository(db_session)
        )

        session_service.create_session(
            call_id=call_id,
            customer_id=None,
        )

        session_service.update_state(
            call_id=call_id,
            state=CallState.END,
        )

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.current_state == (
            CallState.END.value
        )

    finally:
        app.dependency_overrides.clear()

def test_vapi_repeated_ended_webhook_is_idempotent(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.call_event_repository import (
        CallEventRepository,
    )
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.session_repository import (
        SessionRepository,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-repeated-ended-001"

        client = TestClient(app)

        payload = {
            "message": {
                "type": "status-update",
                "call": {
                    "id": call_id,
                    "status": "ended",
                },
            },
        }

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

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.current_state == "END"

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.ended_at is not None

        events = (
            CallEventRepository(db_session)
            .get_by_call_id(call_id)
        )

        ended_events = [
            event
            for event in events
            if event.event_type == "CALL_ENDED"
        ]

        assert len(ended_events) == 1

    finally:
        app.dependency_overrides.clear()

def test_vapi_repeated_ended_webhook_preserves_ended_at(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.session_repository import (
        SessionRepository,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-ended-timestamp-001"

        client = TestClient(app)

        payload = {
            "message": {
                "type": "status-update",
                "call": {
                    "id": call_id,
                    "status": "ended",
                },
            },
        }

        first = client.post(
            "/vapi/webhook",
            json=payload,
            headers=valid_headers(),
        )

        assert first.status_code == 200

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.ended_at is not None

        first_ended_at = call_log.ended_at

        second = client.post(
            "/vapi/webhook",
            json=payload,
            headers=valid_headers(),
        )

        assert second.status_code == 200

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.ended_at == first_ended_at

    finally:
        app.dependency_overrides.clear()

def test_vapi_in_progress_creates_active_call(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.session_repository import (
        SessionRepository,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-active-call-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "ok"
        assert data["event_type"] == "status-update"
        assert data["call_id"] == call_id

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.current_state == "CALL_CONNECTED"

    finally:
        app.dependency_overrides.clear()

def test_vapi_repeated_in_progress_webhook_is_idempotent(
    db_session,
):
    from sqlalchemy import text

    from app.db.database import get_db
    from app.db.repositories.session_repository import (
        SessionRepository,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-repeated-progress-001"

        client = TestClient(app)

        payload = {
            "message": {
                "type": "status-update",
                "call": {
                    "id": call_id,
                    "status": "in-progress",
                },
            },
        }

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

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.current_state == "CALL_CONNECTED"

        session_count = db_session.execute(
            text(
                "SELECT COUNT(*) FROM sessions "
                "WHERE call_id = :call_id"
            ),
            {"call_id": call_id},
        ).scalar_one()

        call_log_count = db_session.execute(
            text(
                "SELECT COUNT(*) FROM call_logs "
                "WHERE call_id = :call_id"
            ),
            {"call_id": call_id},
        ).scalar_one()

        assert session_count == 1
        assert call_log_count == 1

    finally:
        app.dependency_overrides.clear()

def test_vapi_unknown_status_does_not_terminate_call(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from app.state.states import CallState

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-unknown-status-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ringing",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.current_state == (
            CallState.CALL_CONNECTED.value
        )

    finally:
        app.dependency_overrides.clear()

def test_vapi_ended_status_creates_and_terminates_new_call(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.call_event_repository import (
        CallEventRepository,
    )
    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from app.state.states import CallState

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-ended-new-call-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.current_state == (
            CallState.END.value
        )

        events = (
            CallEventRepository(db_session)
            .get_by_call_id(call_id)
        )

        ended_events = [
            event
            for event in events
            if event.event_type == "CALL_ENDED"
        ]

        assert len(ended_events) == 1

    finally:
        app.dependency_overrides.clear()

def test_vapi_ended_webhook_creates_single_call_log(
    db_session,
):
    from sqlalchemy import text

    from app.db.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-ended-single-log-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        count = db_session.execute(
            text(
                "SELECT COUNT(*) FROM call_logs "
                "WHERE call_id = :call_id"
            ),
            {"call_id": call_id},
        ).scalar_one()

        assert count == 1

    finally:
        app.dependency_overrides.clear()

def test_vapi_ended_webhook_creates_single_session(
    db_session,
):
    from sqlalchemy import text

    from app.db.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-ended-single-session-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        count = db_session.execute(
            text(
                "SELECT COUNT(*) FROM sessions "
                "WHERE call_id = :call_id"
            ),
            {"call_id": call_id},
        ).scalar_one()

        assert count == 1

    finally:
        app.dependency_overrides.clear()

def test_vapi_ended_webhook_preserves_customer_id(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.models.customer import Customer

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer = Customer(
            name="VAPI Customer",
            phone="9111111111",
        )

        customer = CustomerRepository(
            db_session
        ).create(customer)

        call_id = "vapi-ended-customer-001"

        client = TestClient(app)

        start_response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer.id,
            },
        )

        assert start_response.status_code == 200

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.customer_id == customer.id

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.customer_id == customer.id

    finally:
        app.dependency_overrides.clear()

def test_vapi_repeated_ended_preserves_customer_id(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from app.models.customer import Customer

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Repeat End Customer",
                phone="9222222222",
            )
        )

        call_id = "vapi-repeat-end-customer-001"

        client = TestClient(app)

        start_response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer.id,
            },
        )

        assert start_response.status_code == 200

        payload = {
            "message": {
                "type": "status-update",
                "call": {
                    "id": call_id,
                    "status": "ended",
                },
            },
        }

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

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.customer_id == customer.id

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.customer_id == customer.id

    finally:
        app.dependency_overrides.clear()

def test_vapi_ended_call_keeps_original_customer_after_duplicate_start(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from app.models.customer import Customer

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer_one = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Original VAPI Customer",
                phone="9333333333",
            )
        )

        customer_two = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Different VAPI Customer",
                phone="9444444444",
            )
        )

        call_id = "vapi-customer-consistency-001"

        client = TestClient(app)

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

        webhook = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert webhook.status_code == 200

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.customer_id == customer_one.id

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.customer_id == customer_one.id

    finally:
        app.dependency_overrides.clear()

def test_duplicate_start_customer_mismatch_does_not_modify_call_log(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.models.customer import Customer

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer_one = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Call Log Original Customer",
                phone="9555555555",
            )
        )

        customer_two = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Call Log Different Customer",
                phone="9666666666",
            )
        )

        call_id = "vapi-log-customer-consistency-001"

        client = TestClient(app)

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

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.customer_id == customer_one.id

    finally:
        app.dependency_overrides.clear()

def test_duplicate_start_customer_mismatch_creates_no_second_session(
    db_session,
):
    from sqlalchemy import text

    from app.db.database import get_db
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.models.customer import Customer

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer_one = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Session Original Customer",
                phone="9777777777",
            )
        )

        customer_two = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Session Different Customer",
                phone="9888888888",
            )
        )

        call_id = "vapi-no-second-session-001"

        client = TestClient(app)

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

        session_count = db_session.execute(
            text(
                "SELECT COUNT(*) FROM sessions "
                "WHERE call_id = :call_id"
            ),
            {"call_id": call_id},
        ).scalar_one()

        assert session_count == 1

    finally:
        app.dependency_overrides.clear()

def test_duplicate_start_customer_mismatch_creates_no_second_call_log(
    db_session,
):
    from sqlalchemy import text

    from app.db.database import get_db
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.models.customer import Customer

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer_one = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Log Count Original Customer",
                phone="9999991001",
            )
        )

        customer_two = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Log Count Different Customer",
                phone="9999991002",
            )
        )

        call_id = "vapi-no-second-call-log-001"

        client = TestClient(app)

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

        call_log_count = db_session.execute(
            text(
                "SELECT COUNT(*) FROM call_logs "
                "WHERE call_id = :call_id"
            ),
            {"call_id": call_id},
        ).scalar_one()

        assert call_log_count == 1

    finally:
        app.dependency_overrides.clear()

def test_duplicate_start_same_customer_remains_idempotent(
    db_session,
):
    from sqlalchemy import text

    from app.db.database import get_db
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.models.customer import Customer

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Same Customer Idempotency",
                phone="9999992001",
            )
        )

        call_id = "vapi-same-customer-idempotent-001"

        client = TestClient(app)

        payload = {
            "call_id": call_id,
            "customer_id": customer.id,
        }

        first = client.post(
            "/calls/start",
            json=payload,
        )

        second = client.post(
            "/calls/start",
            json=payload,
        )

        assert first.status_code == 200
        assert second.status_code == 200

        assert first.json()["call_id"] == call_id
        assert second.json()["call_id"] == call_id

        session_count = db_session.execute(
            text(
                "SELECT COUNT(*) FROM sessions "
                "WHERE call_id = :call_id"
            ),
            {"call_id": call_id},
        ).scalar_one()

        call_log_count = db_session.execute(
            text(
                "SELECT COUNT(*) FROM call_logs "
                "WHERE call_id = :call_id"
            ),
            {"call_id": call_id},
        ).scalar_one()

        assert session_count == 1
        assert call_log_count == 1

    finally:
        app.dependency_overrides.clear()

def test_duplicate_start_same_customer_preserves_customer_association(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from app.models.customer import Customer

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Same Customer Association",
                phone="9999993001",
            )
        )

        call_id = "vapi-same-customer-association-001"

        client = TestClient(app)

        payload = {
            "call_id": call_id,
            "customer_id": customer.id,
        }

        first = client.post(
            "/calls/start",
            json=payload,
        )

        second = client.post(
            "/calls/start",
            json=payload,
        )

        assert first.status_code == 200
        assert second.status_code == 200

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.customer_id == customer.id

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.customer_id == customer.id

    finally:
        app.dependency_overrides.clear()

def test_vapi_ended_preserves_customer_association_after_termination(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from app.models.customer import Customer
    from app.state.states import CallState

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Termination Association Customer",
                phone="9999994001",
            )
        )

        call_id = "vapi-ended-association-001"

        client = TestClient(app)

        start_response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer.id,
            },
        )

        assert start_response.status_code == 200

        ended_response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert ended_response.status_code == 200

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.current_state == (
            CallState.END.value
        )
        assert session.customer_id == customer.id

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.customer_id == customer.id
        assert call_log.ended_at is not None

    finally:
        app.dependency_overrides.clear()

def test_vapi_ended_creates_correct_call_ended_event(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.call_event_repository import (
        CallEventRepository,
    )
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.models.customer import Customer

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="VAPI Event Customer",
                phone="9999995001",
            )
        )

        call_id = "vapi-ended-event-fields-001"

        client = TestClient(app)

        start_response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer.id,
            },
        )

        assert start_response.status_code == 200

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        events = (
            CallEventRepository(db_session)
            .get_by_call_id(call_id)
        )

        ended_events = [
            event
            for event in events
            if event.event_type == "CALL_ENDED"
        ]

        assert len(ended_events) == 1

        event = ended_events[0]

        assert event.call_id == call_id
        assert event.event_type == "CALL_ENDED"
        assert event.from_state is None
        assert event.to_state == "END"

    finally:
        app.dependency_overrides.clear()

def test_vapi_ended_event_has_timestamp(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.call_event_repository import (
        CallEventRepository,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-ended-event-time-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        events = (
            CallEventRepository(db_session)
            .get_by_call_id(call_id)
        )

        ended_events = [
            event
            for event in events
            if event.event_type == "CALL_ENDED"
        ]

        assert len(ended_events) == 1
        assert ended_events[0].created_at is not None

    finally:
        app.dependency_overrides.clear()

def test_vapi_ended_event_is_last_call_event(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.call_event_repository import (
        CallEventRepository,
    )
    from app.state.states import CallState

    from tests.test_call_flow_service import (
        create_service,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-ended-event-order-001"

        service = create_service(db_session)

        machine, _, _ = service.start_call(
            call_id=call_id,
            customer_id=None,
        )

        service.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.INTRODUCTION,
        )

        service.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.CHECK_PERSON,
        )

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        events = (
            CallEventRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert len(events) >= 1

        assert events[-1].event_type == "CALL_ENDED"
        assert events[-1].to_state == "END"

    finally:
        app.dependency_overrides.clear()

def test_vapi_ended_event_is_last_call_event(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.call_event_repository import (
        CallEventRepository,
    )
    from app.state.states import CallState

    from tests.test_call_flow_service import (
        create_service,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-ended-event-order-001"

        service = create_service(db_session)

        machine, _, _ = service.start_call(
            call_id=call_id,
            customer_id=None,
        )

        service.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.INTRODUCTION,
        )

        service.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.CHECK_PERSON,
        )

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        events = (
            CallEventRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert len(events) >= 1

        assert events[-1].event_type == "CALL_ENDED"
        assert events[-1].to_state == "END"

    finally:
        app.dependency_overrides.clear()

def test_vapi_ended_webhook_returns_consistent_response(
    db_session,
):
    from app.db.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-response-contract-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        assert response.json() == {
            "status": "ok",
            "event_type": "status-update",
            "call_id": call_id,
        }

    finally:
        app.dependency_overrides.clear()

def test_vapi_in_progress_webhook_returns_consistent_response(
    db_session,
):
    from app.db.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-progress-response-contract-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        assert response.json() == {
            "status": "ok",
            "event_type": "status-update",
            "call_id": call_id,
        }

    finally:
        app.dependency_overrides.clear()

def test_vapi_unknown_event_returns_consistent_response(
    db_session,
):
    from app.db.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-unknown-response-contract-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "assistant-request",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        assert response.json() == {
            "status": "ok",
            "event_type": "assistant-request",
            "call_id": call_id,
        }

    finally:
        app.dependency_overrides.clear()

def test_vapi_webhook_rejects_invalid_authorization(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.session_repository import (
        SessionRepository,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-invalid-auth-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                },
            },
            headers={
                "Authorization": "Bearer invalid-secret",
            },
        )

        assert response.status_code == 401

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is None

    finally:
        app.dependency_overrides.clear()

def test_vapi_webhook_rejects_missing_authorization(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.session_repository import (
        SessionRepository,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-missing-auth-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                },
            },
        )

        assert response.status_code == 401

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is None

    finally:
        app.dependency_overrides.clear()

def test_vapi_webhook_rejects_wrong_authorization_scheme(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.session_repository import (
        SessionRepository,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-wrong-auth-scheme-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                },
            },
            headers={
                "Authorization": "Basic invalid-secret",
            },
        )

        assert response.status_code == 401

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is None

    finally:
        app.dependency_overrides.clear()

def test_vapi_webhook_rejects_empty_authorization(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.session_repository import (
        SessionRepository,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-empty-auth-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                },
            },
            headers={
                "Authorization": "",
            },
        )

        assert response.status_code == 401

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is None

    finally:
        app.dependency_overrides.clear()

def test_vapi_webhook_rejects_wrong_bearer_secret(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.session_repository import (
        SessionRepository,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-wrong-bearer-secret-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                },
            },
            headers={
                "Authorization": "Bearer definitely-wrong-secret",
            },
        )

        assert response.status_code == 401

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is None

    finally:
        app.dependency_overrides.clear()

def test_vapi_webhook_rejects_bearer_secret_with_trailing_whitespace(
    db_session,
):
    from app.db.database import get_db
    from app.db.repositories.session_repository import (
        SessionRepository,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        from app.core.config import settings

        call_id = "vapi-auth-whitespace-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "status-update",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                },
            },
            headers={
                "Authorization": (
                    f"Bearer {settings.VAPI_WEBHOOK_SECRET} "
                ),
            },
        )

        assert response.status_code == 401

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is None

    finally:
        app.dependency_overrides.clear()

def test_vapi_webhook_rejects_missing_message(
    db_session,
):
    from app.db.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={},
            headers=valid_headers(),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()

def test_vapi_webhook_rejects_missing_message(
    db_session,
):
    from app.db.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={},
            headers=valid_headers(),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()

def test_vapi_webhook_rejects_invalid_message_type(
    db_session,
):
    from app.db.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": "invalid-message",
            },
            headers=valid_headers(),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()

def test_vapi_webhook_rejects_invalid_message_type(
    db_session,
):
    from app.db.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": "invalid-message",
            },
            headers=valid_headers(),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()

def test_vapi_assistant_request_returns_ai_response(
    db_session,
    monkeypatch,
):
    from app.db.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-assistant-ai-001"

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "assistant-request",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                    "content": "I want to make a payment.",
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "ok"
        assert data["event_type"] == "assistant-request"
        assert data["call_id"] == call_id
        assert "response" in data

    finally:
        app.dependency_overrides.clear()


def test_vapi_action_request_executes_ai_action(
    db_session,
    monkeypatch,
):
    from app.db.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-action-request-001"

        expected_result = {
            "extraction": {
                "intent": "PROMISE_TO_PAY",
                "amount": 5000,
                "promise_date": "2026-08-30",
            },
            "result": "PTP_CREATED",
        }

        def fake_handle_ai_action(
            self,
            call_id,
            user_message,
        ):
            assert call_id == "vapi-action-request-001"
            assert user_message == (
                "I will pay 5000 on 30 September 2026."
            )
            return expected_result

        from app.services.vapi_webhook_service import (
            VapiWebhookService,
        )

        monkeypatch.setattr(
            VapiWebhookService,
            "handle_ai_action",
            fake_handle_ai_action,
        )

        client = TestClient(app)

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "action-request",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                    "content": (
                        "I will pay 5000 on 30 September 2026."
                    ),
                },
            },
            headers=valid_headers(),
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "ok"
        assert data["event_type"] == "action-request"
        assert data["call_id"] == call_id
        assert "response" in data

    finally:
        app.dependency_overrides.clear()



def test_vapi_action_request_creates_ptp(
    db_session,
    monkeypatch,
):
    from datetime import date
    from decimal import Decimal

    from app.db.database import get_db
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.db.repositories.loan_repository import (
        LoanRepository,
    )
    from app.db.repositories.promise_to_pay_repository import (
        PromiseToPayRepository,
    )
    from app.models.customer import Customer
    from app.models.loan import Loan
    from app.schemas.conversation_extraction import (
        ConversationExtraction,
    )
    from app.schemas.intent import CustomerIntent
    from app.state.states import CallState

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Vapi PTP Customer",
                phone="9999996001",
            )
        )

        loan = Loan(
            customer_id=customer.id,
            loan_type="PERSONAL",
            overdue_amount=Decimal("5000.00"),
            days_past_due=30,
        )

        db_session.add(loan)
        db_session.commit()
        db_session.refresh(loan)

        call_id = "vapi-action-ptp-001"

        client = TestClient(app)

        start_response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer.id,
            },
        )

        assert start_response.status_code == 200

        from app.api.dependencies import get_call_flow_service
        from tests.test_call_flow_service import create_service

        call_flow_service = create_service(db_session)

        from app.db.repositories.call_event_repository import (
            CallEventRepository,
        )
        from app.services.call_event_service import (
            CallEventService,
        )

        call_flow_service.call_event_service = (
            CallEventService(
                CallEventRepository(db_session)
            )
        )

        app.dependency_overrides[
            get_call_flow_service
        ] = lambda: call_flow_service

        machine = call_flow_service.restore_machine(call_id)

        for next_state in (
            CallState.INTRODUCTION,
            CallState.CHECK_PERSON,
            CallState.AUTHENTICATION,
            CallState.DISCLOSE_OVERDUE,
            CallState.INTENT_HANDLING,
        ):
            call_flow_service.transition(
                call_id=call_id,
                machine=machine,
                next_state=next_state,
            )

        extraction = ConversationExtraction(
            intent=CustomerIntent.PROMISE_TO_PAY,
            amount=Decimal("5000"),
            promise_date=date(2026, 9, 30),
        )

        def fake_extract(
            self,
            user_message,
        ):
            assert user_message == (
                "I will pay 5000 on 30 September 2026."
            )
            return extraction

        from app.services.conversation_extraction_service import (
            ConversationExtractionService,
        )

        monkeypatch.setattr(
            ConversationExtractionService,
            "extract",
            fake_extract,
        )

        response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "action-request",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                    "content": (
                        "I will pay 5000 on 30 September 2026."
                    ),
                },
            },
            headers=valid_headers(),
        )


        assert response.status_code == 200

        ptps = PromiseToPayRepository(
            db_session
        ).get_by_customer_id(customer.id)

        assert len(ptps) == 1

        ptp = ptps[0]

        assert ptp.customer_id == customer.id
        assert ptp.loan_id == loan.id
        assert ptp.amount == Decimal("5000.00")
        assert ptp.promise_date == date(2026, 9, 30)

        from app.db.repositories.session_repository import (
            SessionRepository,
        )

        session = SessionRepository(
            db_session
        ).get_by_call_id(call_id)

        assert session is not None
        assert session.current_state == (
            CallState.DISPOSITION.value
        )

        end_response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "end-of-call-report",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert end_response.status_code == 200

        end_data = end_response.json()

        assert end_data["status"] == "ok"
        assert (
            end_data["event_type"]
            == "end-of-call-report"
        )
        assert end_data["call_id"] == call_id

        final_session = (
            call_flow_service
            .session_service
            .get_session(call_id)
        )

        assert final_session is not None
        assert final_session.current_state == (
            CallState.END.value
        )

        from app.db.repositories.call_event_repository import (
            CallEventRepository,
        )
        from app.db.repositories.call_log_repository import (
            CallLogRepository,
        )

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.ended_at is not None

        events = (
            CallEventRepository(db_session)
            .get_by_call_id(call_id)
        )

        ended_events = [
            event
            for event in events
            if event.event_type == "CALL_ENDED"
        ]

        assert len(ended_events) == 1

    finally:
        app.dependency_overrides.clear()














def test_vapi_complete_ptp_conversation_lifecycle(
    db_session,
    monkeypatch,
):
    from datetime import date
    from decimal import Decimal

    from fastapi.testclient import TestClient

    from app.api.dependencies import get_call_flow_service
    from app.db.database import get_db
    from app.db.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.db.repositories.loan_repository import (
        LoanRepository,
    )
    from app.db.repositories.promise_to_pay_repository import (
        PromiseToPayRepository,
    )
    from app.models.customer import Customer
    from app.models.loan import Loan
    from app.schemas.conversation_extraction import (
        ConversationExtraction,
    )
    from app.schemas.intent import CustomerIntent
    from app.main import app
    from app.state.states import CallState
    from tests.test_call_flow_service import create_service

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        customer = CustomerRepository(
            db_session
        ).create(
            Customer(
                name="Vapi E2E Customer",
                phone="9999996002",
            )
        )

        loan = Loan(
            customer_id=customer.id,
            loan_type="PERSONAL",
            overdue_amount=Decimal("5000.00"),
            days_past_due=30,
        )

        db_session.add(loan)
        db_session.commit()
        db_session.refresh(loan)

        call_id = "vapi-e2e-ptp-001"

        client = TestClient(app)

        start_response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer.id,
            },
        )

        assert start_response.status_code == 200

        call_flow_service = create_service(db_session)

        from app.db.repositories.call_event_repository import (
            CallEventRepository,
        )
        from app.services.call_event_service import (
            CallEventService,
        )

        call_flow_service.call_event_service = (
            CallEventService(
                CallEventRepository(db_session)
            )
        )

        app.dependency_overrides[
            get_call_flow_service
        ] = lambda: call_flow_service

        machine = call_flow_service.restore_machine(
            call_id
        )

        for next_state in (
            CallState.INTRODUCTION,
            CallState.CHECK_PERSON,
            CallState.AUTHENTICATION,
            CallState.DISCLOSE_OVERDUE,
            CallState.INTENT_HANDLING,
        ):
            call_flow_service.transition(
                call_id=call_id,
                machine=machine,
                next_state=next_state,
            )

        class FakeAIConversationService:
            def generate_response(
                self,
                user_message,
                current_state=None,
            ):
                assert current_state == (
                    CallState.INTENT_HANDLING.value
                )
                assert user_message == (
                    "I want to make a payment."
                )

                return (
                    "Sure. How much would you like "
                    "to pay and on what date?"
                )

        def fake_extract(
            self,
            user_message,
        ):
            assert user_message == (
                "I will pay 5000 on 30 September 2026."
            )

            return ConversationExtraction(
                intent=CustomerIntent.PROMISE_TO_PAY,
                amount=Decimal("5000"),
                promise_date=date(2026, 9, 30),
            )

        from app.services.ai_conversation_service import (
            AIConversationService,
        )
        from app.services.conversation_extraction_service import (
            ConversationExtractionService,
        )

        monkeypatch.setattr(
            AIConversationService,
            "generate_response",
            FakeAIConversationService().generate_response,
        )

        monkeypatch.setattr(
            ConversationExtractionService,
            "extract",
            fake_extract,
        )

        assistant_response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "assistant-request",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                    "content": (
                        "I want to make a payment."
                    ),
                },
            },
            headers=valid_headers(),
        )

        assert assistant_response.status_code == 200

        assistant_data = assistant_response.json()

        assert assistant_data["status"] == "ok"
        assert (
            assistant_data["event_type"]
            == "assistant-request"
        )
        assert assistant_data["call_id"] == call_id
        assert assistant_data["response"] == (
            "Sure. How much would you like "
            "to pay and on what date?"
        )

        action_response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "action-request",
                    "call": {
                        "id": call_id,
                        "status": "in-progress",
                    },
                    "content": (
                        "I will pay 5000 on "
                        "30 September 2026."
                    ),
                },
            },
            headers=valid_headers(),
        )

        assert action_response.status_code == 200

        action_data = action_response.json()

        assert action_data["status"] == "ok"
        assert (
            action_data["event_type"]
            == "action-request"
        )
        assert action_data["call_id"] == call_id
        assert "PTP_COMMITTED" in (
            action_data["response"]
        )

        ptps = PromiseToPayRepository(
            db_session
        ).get_by_customer_id(customer.id)

        assert len(ptps) == 1

        ptp = ptps[0]

        assert ptp.customer_id == customer.id
        assert ptp.loan_id == loan.id
        assert ptp.amount == Decimal("5000.00")
        assert ptp.promise_date == date(2026, 9, 30)

        session = (
            call_flow_service
            .session_service
            .get_session(call_id)
        )

        assert session is not None
        assert session.current_state == (
            CallState.DISPOSITION.value
        )

        end_response = client.post(
            "/vapi/webhook",
            json={
                "message": {
                    "type": "end-of-call-report",
                    "call": {
                        "id": call_id,
                        "status": "ended",
                    },
                },
            },
            headers=valid_headers(),
        )

        assert end_response.status_code == 200

        end_data = end_response.json()

        assert end_data["status"] == "ok"
        assert (
            end_data["event_type"]
            == "end-of-call-report"
        )
        assert end_data["call_id"] == call_id

        final_session = (
            call_flow_service
            .session_service
            .get_session(call_id)
        )

        assert final_session is not None
        assert final_session.current_state == (
            CallState.END.value
        )

        from app.db.repositories.call_event_repository import (
            CallEventRepository,
        )
        from app.db.repositories.call_log_repository import (
            CallLogRepository,
        )

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.ended_at is not None

        events = (
            CallEventRepository(db_session)
            .get_by_call_id(call_id)
        )

        ended_events = [
            event
            for event in events
            if event.event_type == "CALL_ENDED"
        ]

        assert len(ended_events) == 1

    finally:
        app.dependency_overrides.clear()






def test_vapi_duplicate_action_request_is_ignored(
    db_session,
    monkeypatch,
):
    from app.db.database import get_db
    from app.services.vapi_webhook_service import (
        VapiWebhookService,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        call_id = "vapi-idempotency-action-001"
        event_id = "vapi-event-duplicate-001"

        expected_result = {
            "extraction": {
                "intent": "PROMISE_TO_PAY",
                "amount": 5000,
                "promise_date": "2026-09-30",
            },
            "result": "PTP_CREATED",
        }

        call_count = 0

        def fake_handle_ai_action(
                self,
                call_id,
                user_message,
            ):
                nonlocal call_count

                call_count += 1

                assert call_id == "vapi-idempotency-action-001"
                assert user_message == (
                    "I will pay 5000 on 30 September 2026."
                )

                return expected_result

        monkeypatch.setattr(
            VapiWebhookService,
            "handle_ai_action",
            fake_handle_ai_action,
        )

        client = TestClient(app)

        payload = {
            "message": {
                "id": event_id,
                "type": "action-request",
                "call": {
                    "id": call_id,
                    "status": "in-progress",
                },
                "content": (
                    "I will pay 5000 on 30 September 2026."
                ),
            },
        }

        first_response = client.post(
            "/vapi/webhook",
            json=payload,
            headers=valid_headers(),
        )

        assert first_response.status_code == 200

        first_data = first_response.json()

        assert first_data["status"] == "ok"
        assert first_data["event_type"] == "action-request"
        assert first_data["call_id"] == call_id

        second_response = client.post(
            "/vapi/webhook",
            json=payload,
            headers=valid_headers(),
        )

        assert second_response.status_code == 200

        second_data = second_response.json()

        assert second_data["status"] == "duplicate"
        assert second_data["event_type"] == "action-request"
        assert second_data["call_id"] == call_id

        assert call_count == 1

    finally:
        app.dependency_overrides.clear()



