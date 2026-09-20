from app.db.repositories.session_repository import (
    SessionRepository,
)
from app.models.session import Session


def test_session_repository_can_be_created(db_session):
    repository = SessionRepository(db_session)

    assert repository is not None


def test_session_repository_can_create_session(
    db_session,
):
    repository = SessionRepository(db_session)

    session = Session(
        call_id="session_test_001",
        customer_id=None,
        authenticated=False,
        current_state="CALL_CONNECTED",
    )

    result = repository.create(session)

    assert result.id is not None
    assert result.call_id == "session_test_001"
    assert result.authenticated is False
    assert result.current_state == "CALL_CONNECTED"


def test_session_repository_can_find_by_call_id(
    db_session,
):
    repository = SessionRepository(db_session)

    session = Session(
        call_id="session_test_002",
        customer_id=None,
        authenticated=False,
        current_state="INTRODUCTION",
    )

    repository.create(session)

    result = repository.get_by_call_id(
        "session_test_002"
    )

    assert result is not None
    assert result.call_id == "session_test_002"
    assert result.current_state == "INTRODUCTION"


def test_session_repository_returns_none_for_unknown_call(
    db_session,
):
    repository = SessionRepository(db_session)

    result = repository.get_by_call_id(
        "does_not_exist"
    )

    assert result is None


def test_session_repository_can_update_session(
    db_session,
):
    repository = SessionRepository(db_session)

    session = Session(
        call_id="session_test_003",
        customer_id=None,
        authenticated=False,
        current_state="CALL_CONNECTED",
    )

    repository.create(session)

    session.authenticated = True
    session.current_state = "AUTHENTICATION"

    result = repository.update(session)

    assert result.authenticated is True
    assert result.current_state == "AUTHENTICATION"