from pydantic import BaseModel, Field


class VapiCall(BaseModel):
    id: str = Field(min_length=1)
    status: str | None = None


class VapiMessage(BaseModel):
    type: str
    call: VapiCall
    content: str | None = None
    id: str | None = None


class VapiWebhookRequest(BaseModel):
    message: VapiMessage


class VapiWebhookResponse(BaseModel):
    status: str
    event_type: str
    call_id: str
    response: str | None = None
