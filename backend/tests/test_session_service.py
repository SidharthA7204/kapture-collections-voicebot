from app.db.repositories.session_repository import (
    SessionRepository,
)
from app.services.session_service import SessionService
from app.state.states import CallState


def create_service(db_session):
    repository = SessionRepository(db_session)

    return SessionService(repository)


def test_session_service_can_be_created(db_session):
    service = create_service(db_session)

    assert service is not None


def test_create_session(db_session):
    service = create_service(db_session)

    result = service.create_session(
        call_id="service_session_001",
        customer_id=None,
    )

    assert result.id is not None
    assert result.call_id == "service_session_001"
    assert result.authenticated is False
    assert (
        result.current_state
        == CallState.CALL_CONNECTED.value
    )


def test_get_session(db_session):
    service = create_service(db_session)

    service.create_session(
        call_id="service_session_002",
        customer_id=None,
    )

    result = service.get_session(
        "service_session_002"
    )

    assert result is not None
    assert result.call_id == "service_session_002"


def test_authenticate_session(db_session):
    service = create_service(db_session)

    service.create_session(
        call_id="service_session_003",
        customer_id=None,
    )

    result = service.authenticate(
        "service_session_003"
    )

    assert result.authenticated is True


def test_update_session_state(db_session):
    service = create_service(db_session)

    service.create_session(
        call_id="service_session_004",
        customer_id=None,
    )

    result = service.update_state(
        "service_session_004",
        CallState.INTRODUCTION,
    )

    assert (
        result.current_state
        == CallState.INTRODUCTION.value
    )


def test_authenticate_requires_existing_session(
    db_session,
):
    service = create_service(db_session)

    try:
        service.authenticate("missing_session")
        assert False
    except ValueError as exc:
        assert "Session not found" in str(exc)


def test_update_state_requires_existing_session(
    db_session,
):
    service = create_service(db_session)

    try:
        service.update_state(
            "missing_session",
            CallState.INTRODUCTION,
        )
        assert False
    except ValueError as exc:
        assert "Session not found" in str(exc)