from pydantic import BaseModel


class AuthenticateCallResponse(BaseModel):
    call_id: str
    authenticated: bool
    current_state: str