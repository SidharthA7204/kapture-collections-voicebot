from datetime import datetime

from pydantic import BaseModel


class CallEventResponse(BaseModel):
    id: int
    call_id: str
    event_type: str
    from_state: str | None
    to_state: str | None
    created_at: datetime


class CallEventsResponse(BaseModel):
    call_id: str
    events: list[CallEventResponse]