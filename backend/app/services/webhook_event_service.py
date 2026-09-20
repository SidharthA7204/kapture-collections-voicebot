from app.db.repositories.webhook_event_repository import (
    WebhookEventRepository,
)
from app.models.webhook_event import WebhookEvent


class WebhookEventService:

    def __init__(
        self,
        repository: WebhookEventRepository,
    ):
        self.repository = repository

    def already_processed(
        self,
        provider: str,
        event_id: str,
    ) -> bool:
        return (
            self.repository.get_by_event_id(
                provider=provider,
                event_id=event_id,
            )
            is not None
        )

    def mark_processed(
        self,
        provider: str,
        event_id: str,
        event_type: str,
        call_id: str,
    ) -> bool:
        event = WebhookEvent(
            provider=provider,
            event_id=event_id,
            event_type=event_type,
            call_id=call_id,
        )

        created = self.repository.create(event)

        return created is not None
