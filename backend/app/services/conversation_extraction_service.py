import json
import re
from datetime import date, datetime
from decimal import Decimal

from app.schemas.conversation_extraction import (
    ConversationExtraction,
)
from app.schemas.intent import CustomerIntent
from app.services.groq_service import GroqService


class ConversationExtractionService:

    EXTRACTION_PROMPT = """
You are a financial collections conversation analyzer.

Analyze ONLY the customer's latest message.

Allowed intents:
- PAY_NOW
- PROMISE_TO_PAY
- DISPUTE
- UNABLE_TO_PAY
- UNKNOWN

Extract:
- amount: payment amount explicitly stated by the customer
- promise_date: date on which the customer explicitly promises/intends to make payment

Return ONLY valid JSON.

Rules:
1. Do not invent missing information.
2. If amount is not explicitly stated, return null.
3. If promise_date is not explicitly stated, return null.
4. Convert explicit dates to YYYY-MM-DD.
5. "September 30", "30 September", and "on September 30"
   are explicit payment dates.
6. If a specific amount and specific payment date are stated,
   intent MUST be PROMISE_TO_PAY.
7. Do not confuse today's date with the promised payment date.

Example:
"I will pay 5000 on September 30."

{
  "intent": "PROMISE_TO_PAY",
  "amount": "5000.00",
  "promise_date": "2026-09-30"
}
"""

    def __init__(
        self,
        groq_service: GroqService,
    ):
        self.groq_service = groq_service

    def _extract_explicit_date(
        self,
        user_message: str,
    ) -> date | None:

        current_year = date.today().year

        # Example:
        # September 30
        # September 30, 2026
        # Sep 30
        # Sep 30, 2026
        month_pattern = (
            r"\b("
            r"January|February|March|April|May|June|July|August|"
            r"September|October|November|December|"
            r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
            r")"
            r"\s+"
            r"(\d{1,2})"
            r"(?:st|nd|rd|th)?"
            r"(?:,\s*|\s+)?"
            r"(\d{4})?"
            r"\b"
        )

        match = re.search(
            month_pattern,
            user_message,
            re.IGNORECASE,
        )

        if match:
            month_name = match.group(1)
            day = int(match.group(2))
            year = (
                int(match.group(3))
                if match.group(3)
                else current_year
            )

            normalized = f"{month_name} {day} {year}"

            for fmt in (
                "%B %d %Y",
                "%b %d %Y",
            ):
                try:
                    return datetime.strptime(
                        normalized,
                        fmt,
                    ).date()
                except ValueError:
                    continue

        # Example:
        # 30 September
        # 30 September 2026
        day_month_pattern = (
            r"\b"
            r"(\d{1,2})"
            r"(?:st|nd|rd|th)?"
            r"\s+"
            r"(January|February|March|April|May|June|July|August|"
            r"September|October|November|December|"
            r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
            r"(?:\s+(\d{4}))?"
            r"\b"
        )

        match = re.search(
            day_month_pattern,
            user_message,
            re.IGNORECASE,
        )

        if match:
            day = int(match.group(1))
            month_name = match.group(2)
            year = (
                int(match.group(3))
                if match.group(3)
                else current_year
            )

            normalized = f"{month_name} {day} {year}"

            for fmt in (
                "%B %d %Y",
                "%b %d %Y",
            ):
                try:
                    return datetime.strptime(
                        normalized,
                        fmt,
                    ).date()
                except ValueError:
                    continue

        return None

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

        extracted_date = self._extract_explicit_date(
            user_message
        )

        llm_date = (
            date.fromisoformat(data["promise_date"])
            if data.get("promise_date") is not None
            else None
        )

        promise_date = extracted_date or llm_date

        return ConversationExtraction(
            intent=CustomerIntent(data["intent"]),
            amount=(
                Decimal(str(data["amount"]))
                if data.get("amount") is not None
                else None
            ),
            promise_date=promise_date,
        )
