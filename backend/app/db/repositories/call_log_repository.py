from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.call_log import CallLog


class CallLogRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_call_id(
        self,
        call_id: str,
    ) -> CallLog | None:
        statement = select(CallLog).where(
            CallLog.call_id == call_id
        )

        return self.db.scalar(statement)

    def create(
        self,
        call_log: CallLog,
        commit: bool = True,
    ) -> CallLog:
        self.db.add(call_log)

        if commit:
            self.db.commit()
            self.db.refresh(call_log)

        return call_log

    def update(
        self,
        call_log: CallLog,
        commit: bool = True,
    ) -> CallLog:
        if commit:
            self.db.commit()
            self.db.refresh(call_log)

        return call_log
