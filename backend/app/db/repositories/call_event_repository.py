from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.call_event import CallEvent


class CallEventRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        event: CallEvent,
        commit: bool = True,
    ) -> CallEvent:
        self.db.add(event)

        if commit:
            self.db.commit()
            self.db.refresh(event)

        return event

    def get_by_call_id(
        self,
        call_id: str,
    ) -> list[CallEvent]:
        statement = (
            select(CallEvent)
            .where(CallEvent.call_id == call_id)
            .order_by(CallEvent.created_at)
        )

        return list(self.db.scalars(statement).all())
