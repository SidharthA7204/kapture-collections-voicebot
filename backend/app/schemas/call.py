from pydantic import BaseModel


class StartCallRequest(BaseModel):
    call_id: str
    customer_id: int | None = None


class StartCallResponse(BaseModel):
    call_id: str
    customer_id: int | None
    current_state: str
    authenticated: bool