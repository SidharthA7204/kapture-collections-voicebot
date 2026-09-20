from pydantic import BaseModel

from app.state.states import CallState


class TransitionCallRequest(BaseModel):
    next_state: CallState


class TransitionCallResponse(BaseModel):
    call_id: str
    current_state: CallState