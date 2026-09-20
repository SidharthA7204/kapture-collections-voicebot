from datetime import date
from decimal import Decimal

from app.schemas.conversation_extraction import (
    ConversationExtraction,
)
from app.schemas.intent_action import IntentAction
from app.services.call_flow_service import CallFlowService
from app.services.ai_intent_service import AIIntentService


class AIActionService:

    def __init__(
        self,
        intent_service: AIIntentService,
        call_flow_service: CallFlowService,
    ):
        self.intent_service = intent_service
        self.call_flow_service = call_flow_service

    def execute(
        self,
        call_id: str,
        customer_id: int | None,
        loan_id: int | None,
        machine,
        extraction: ConversationExtraction,
    ):
        action = self.intent_service.determine_action(
            extraction
        )

        return self.call_flow_service.handle_action(
            call_id=call_id,
            machine=machine,
            action=action,
            customer_id=customer_id,
            loan_id=loan_id,
            amount=extraction.amount,
            promise_date=extraction.promise_date,
        )
