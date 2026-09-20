from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.webhook_event import WebhookEvent


class WebhookEventRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_event_id(
        self,
        provider: str,
        event_id: str,
    ) -> WebhookEvent | None:
        statement = (
            select(WebhookEvent)
            .where(
                WebhookEvent.provider == provider,
                WebhookEvent.event_id == event_id,
            )
        )

        return self.db.scalars(statement).first()

    def create(
        self,
        event: WebhookEvent,
    ) -> WebhookEvent | None:
        try:
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            return event

        except IntegrityError:
            self.db.rollback()
            return None
