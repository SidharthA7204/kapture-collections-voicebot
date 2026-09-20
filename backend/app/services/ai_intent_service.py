from app.schemas.conversation_extraction import (
    ConversationExtraction,
)
from app.schemas.intent_action import IntentAction
from app.services.intent_service import IntentService


class AIIntentService:

    def __init__(
        self,
        intent_service: IntentService,
    ):
        self.intent_service = intent_service

    def determine_action(
        self,
        extraction: ConversationExtraction,
    ) -> IntentAction:
        return self.intent_service.determine_action(
            extraction.intent
        )
