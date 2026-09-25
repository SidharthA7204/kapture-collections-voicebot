from app.core.config import settings
from app.db.database import Base, engine


def test_database_configuration():

    assert settings.DATABASE_URL
    assert engine is not None
    assert Base is not None
def test_database_session_can_rollback_after_integrity_error(
    db_session,
):
    from sqlalchemy.exc import IntegrityError

    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from app.models.session import Session

    repository = SessionRepository(db_session)

    first = Session(
        call_id="rollback-test-001",
        customer_id=None,
        current_state="START",
        authenticated=False,
        verification_attempts=0,
    )

    repository.create(first)

    duplicate = Session(
        call_id="rollback-test-001",
        customer_id=None,
        current_state="START",
        authenticated=False,
        verification_attempts=0,
    )

    db_session.add(duplicate)

    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
    else:
        raise AssertionError(
            "Expected IntegrityError was not raised"
        )

    existing = repository.get_by_call_id(
        "rollback-test-001"
    )

    assert existing is not None
    assert existing.call_id == "rollback-test-001"

def test_call_start_creates_session_and_call_log_consistently(
    db_session,
):
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from tests.test_call_flow_service import create_service

    call_id = "transaction-consistency-001"

    service = create_service(db_session)

    machine, session, call_log = service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    stored_session = (
        SessionRepository(db_session)
        .get_by_call_id(call_id)
    )

    stored_call_log = (
        CallLogRepository(db_session)
        .get_by_call_id(call_id)
    )

    assert stored_session is not None
    assert stored_call_log is not None

    assert stored_session.call_id == call_id
    assert stored_call_log.call_id == call_id

    assert session.call_id == call_id
    assert call_log.call_id == call_id

    assert machine is not None

def test_call_start_duplicate_does_not_create_second_records(
    db_session,
):
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from tests.test_call_flow_service import create_service

    call_id = "transaction-duplicate-001"

    service = create_service(db_session)

    service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    sessions = (
        db_session.query(
            SessionRepository(db_session).db.get_bind()
        )
        if False
        else None
    )

    session = (
        SessionRepository(db_session)
        .get_by_call_id(call_id)
    )

    call_log = (
        CallLogRepository(db_session)
        .get_by_call_id(call_id)
    )

    assert session is not None
    assert call_log is not None

    session_count = (
        db_session.query(
            type(session)
        )
        .filter_by(call_id=call_id)
        .count()
    )

    call_log_count = (
        db_session.query(
            type(call_log)
        )
        .filter_by(call_id=call_id)
        .count()
    )

    assert session_count == 1
    assert call_log_count == 1

def test_database_session_is_reusable_after_rollback(
    db_session,
):
    from sqlalchemy.exc import IntegrityError

    from app.db.repositories.session_repository import (
        SessionRepository,
    )
    from app.models.session import Session

    repository = SessionRepository(db_session)

    call_id = "rollback-reuse-001"

    repository.create(
        Session(
            call_id=call_id,
            customer_id=None,
            current_state="START",
            authenticated=False,
            verification_attempts=0,
        )
    )

    duplicate = Session(
        call_id=call_id,
        customer_id=None,
        current_state="START",
        authenticated=False,
        verification_attempts=0,
    )

    db_session.add(duplicate)

    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()

    recovered = repository.get_by_call_id(call_id)

    assert recovered is not None
    assert recovered.call_id == call_id

    new_call_id = "rollback-reuse-002"

    new_session = repository.create(
        Session(
            call_id=new_call_id,
            customer_id=None,
            current_state="START",
            authenticated=False,
            verification_attempts=0,
        )
    )

    assert new_session.call_id == new_call_id

    assert (
        repository.get_by_call_id(new_call_id)
        is not None
    )

def test_database_pool_configuration():
    assert engine.pool.size() == settings.DB_POOL_SIZE
    assert engine.pool._max_overflow == settings.DB_MAX_OVERFLOW
    assert engine.pool._timeout == settings.DB_POOL_TIMEOUT
    assert engine.pool._recycle == settings.DB_POOL_RECYCLE


def test_database_pool_uses_pre_ping():
    assert engine.pool._pre_ping is True
