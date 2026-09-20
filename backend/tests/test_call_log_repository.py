from datetime import datetime

from app.db.repositories.call_log_repository import (
    CallLogRepository,
)
from app.models.call_log import CallLog


def test_call_log_repository_can_be_created(db_session):
    repository = CallLogRepository(db_session)

    assert repository is not None


def test_call_log_repository_can_create_call_log(
    db_session,
):
    repository = CallLogRepository(db_session)

    call_log = CallLog(
        call_id="repo_test_001",
        customer_id=None,
        disposition="PAYMENT_INITIATED",
        started_at=datetime.utcnow(),
    )

    result = repository.create(call_log)

    assert result.id is not None
    assert result.call_id == "repo_test_001"
    assert result.disposition == "PAYMENT_INITIATED"


def test_call_log_repository_can_find_by_call_id(
    db_session,
):
    repository = CallLogRepository(db_session)

    call_log = CallLog(
        call_id="repo_test_002",
        customer_id=None,
        disposition="PTP_COMMITTED",
        started_at=datetime.utcnow(),
    )

    repository.create(call_log)

    result = repository.get_by_call_id(
        "repo_test_002"
    )

    assert result is not None
    assert result.call_id == "repo_test_002"
    assert result.disposition == "PTP_COMMITTED"


def test_call_log_repository_returns_none_for_unknown_call(
    db_session,
):
    repository = CallLogRepository(db_session)

    result = repository.get_by_call_id(
        "does_not_exist"
    )

    assert result is None