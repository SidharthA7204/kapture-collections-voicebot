from pydantic import BaseModel


class CallTerminationResponse(BaseModel):
    call_id: str
    current_state: str