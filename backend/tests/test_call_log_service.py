from app.db.repositories.call_log_repository import (
    CallLogRepository,
)
from app.services.call_log_service import CallLogService


def create_service(db_session):
    repository = CallLogRepository(db_session)

    return CallLogService(repository)


def test_call_log_service_can_be_created(db_session):
    service = create_service(db_session)

    assert service is not None


def test_start_call_creates_call_log(db_session):
    service = create_service(db_session)

    result = service.start_call(
        call_id="service_test_001",
        customer_id=None,
    )

    assert result.id is not None
    assert result.call_id == "service_test_001"
    assert result.started_at is not None
    assert result.ended_at is None


def test_record_disposition_updates_call_log(
    db_session,
):
    service = create_service(db_session)

    service.start_call(
        call_id="service_test_002",
        customer_id=None,
    )

    result = service.record_disposition(
        call_id="service_test_002",
        disposition="PAYMENT_INITIATED",
    )

    assert result.disposition == "PAYMENT_INITIATED"


def test_end_call_records_end_time(db_session):
    service = create_service(db_session)

    service.start_call(
        call_id="service_test_003",
        customer_id=None,
    )

    result = service.end_call(
        call_id="service_test_003",
    )

    assert result.ended_at is not None


def test_record_disposition_requires_existing_call(
    db_session,
):
    service = create_service(db_session)

    try:
        service.record_disposition(
            call_id="missing_call",
            disposition="PAYMENT_INITIATED",
        )
        assert False
    except ValueError as exc:
        assert "Call log not found" in str(exc)


def test_end_call_requires_existing_call(db_session):
    service = create_service(db_session)

    try:
        service.end_call(
            call_id="missing_call",
        )
        assert False
    except ValueError as exc:
        assert "Call log not found" in str(exc)