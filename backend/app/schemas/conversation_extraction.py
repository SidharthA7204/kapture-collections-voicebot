from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.intent import CustomerIntent


class ConversationExtraction(BaseModel):
    intent: CustomerIntent

    amount: Decimal | None = Field(
        default=None,
        gt=0,
    )

    promise_date: date | None = None
