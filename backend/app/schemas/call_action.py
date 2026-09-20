from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.intent_action import IntentAction


class CallActionRequest(BaseModel):
    action: IntentAction

    customer_id: int | None = None
    loan_id: int | None = None
    amount: Decimal | None = Field(
        default=None,
        gt=0,
    )
    promise_date: date | None = None


class CallActionResponse(BaseModel):
    call_id: str
    disposition: str
