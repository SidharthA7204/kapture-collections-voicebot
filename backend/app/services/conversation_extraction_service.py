import json
from datetime import date
from decimal import Decimal

from app.schemas.conversation_extraction import (
    ConversationExtraction,
)
from app.schemas.intent import CustomerIntent
from app.services.groq_service import GroqService


class ConversationExtractionService:

    EXTRACTION_PROMPT = """
You are a financial collections conversation analyzer.

Analyze the customer's latest message and determine their intent.

Allowed intents:
- PAY_NOW
- PROMISE_TO_PAY
- DISPUTE
- UNABLE_TO_PAY
- UNKNOWN

Extract:
- amount: payment amount if explicitly stated
- promise_date: promised payment date if explicitly stated

Rules:
1. Return ONLY valid JSON.
2. Do not include markdown.
3. Do not invent missing information.
4. If amount is not stated, use null.
5. If promise date is not stated, use null.
6. Use ISO date format YYYY-MM-DD.
7. For PROMISE_TO_PAY, extract both amount and date when available.

Example:

Customer:
"I will pay 5000 on 30 August 2026."

Return:
{
  "intent": "PROMISE_TO_PAY",
  "amount": "5000.00",
  "promise_date": "2026-08-30"
}
"""

    def __init__(
        self,
        groq_service: GroqService,
    ):
        self.groq_service = groq_service

    def extract(
        self,
        user_message: str,
    ) -> ConversationExtraction:

        if not user_message.strip():
            raise ValueError(
                "User message cannot be empty."
            )

        response = self.groq_service.generate_response(
            system_prompt=self.EXTRACTION_PROMPT,
            user_message=user_message,
        )

        try:
            data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid extraction JSON."
            ) from exc

        return ConversationExtraction(
            intent=CustomerIntent(data["intent"]),
            amount=(
                Decimal(str(data["amount"]))
                if data.get("amount") is not None
                else None
            ),
            promise_date=(
                date.fromisoformat(data["promise_date"])
                if data.get("promise_date") is not None
                else None
            ),
        )
