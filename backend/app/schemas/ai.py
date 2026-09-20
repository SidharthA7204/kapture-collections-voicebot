from pydantic import BaseModel, Field

from app.schemas.conversation_extraction import (
    ConversationExtraction,
)
from app.schemas.intent_action import IntentAction


class AIChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )

    current_state: str | None = None


class AIChatResponse(BaseModel):
    response: str


class AIExtractionRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )


class AIExtractionResponse(BaseModel):
    extraction: ConversationExtraction


class AIAnalyzeRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )


class AIAnalyzeResponse(BaseModel):
    extraction: ConversationExtraction
    action: IntentAction


class AIExecuteRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )

    call_id: str = Field(
        min_length=1,
        max_length=128,
    )

    customer_id: int | None = None
    loan_id: int | None = None


class AIExecuteResponse(BaseModel):
    call_id: str
    extraction: ConversationExtraction
    action: IntentAction
    disposition: str
