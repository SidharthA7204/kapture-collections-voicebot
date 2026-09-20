from datetime import datetime

from app.models.call_log import CallLog
from app.db.repositories.call_log_repository import CallLogRepository


class CallLogService:

    def __init__(
        self,
        repository: CallLogRepository,
    ):
        self.repository = repository

    def start_call(
        self,
        call_id: str,
        customer_id: int | None = None,
    ) -> CallLog:
        call_log = CallLog(
            call_id=call_id,
            customer_id=customer_id,
            started_at=datetime.utcnow(),
        )

        return self.repository.create(call_log)

    def get_call_log(
        self,
        call_id: str,
    ) -> CallLog | None:
        return self.repository.get_by_call_id(call_id)

    def record_disposition(
        self,
        call_id: str,
        disposition: str,
        commit: bool = True,
    ) -> CallLog:
        call_log = self.repository.get_by_call_id(call_id)

        if call_log is None:
            raise ValueError(
                f"Call log not found: {call_id}"
            )

        call_log.disposition = disposition

        return self.repository.update(
            call_log,
            commit=commit,
        )

    def end_call(
        self,
        call_id: str,
    ) -> CallLog:
        call_log = self.repository.get_by_call_id(call_id)

        if call_log is None:
            raise ValueError(
                f"Call log not found: {call_id}"
            )

        call_log.ended_at = datetime.utcnow()

        return self.repository.update(call_log)
