from app.core.voice_metrics import VOICE_CALLS_ENDED_TOTAL
from app.db.repositories.call_event_repository import (
    CallEventRepository,
)
from app.models.call_event import CallEvent


class CallEventService:

    def __init__(
        self,
        repository: CallEventRepository,
    ):
        self.repository = repository

    def record_state_change(
        self,
        call_id: str,
        from_state: str,
        to_state: str,
        commit: bool = True,
    ) -> CallEvent:
        event = CallEvent(
            call_id=call_id,
            event_type="STATE_CHANGED",
            from_state=from_state,
            to_state=to_state,
        )

        return self.repository.create(
            event,
            commit=commit,
        )

    def record_state_transition(
        self,
        call_id: str,
        from_state,
        to_state,
    ) -> CallEvent:
        return self.record_state_change(
            call_id=call_id,
            from_state=(
                from_state.value
                if hasattr(from_state, "value")
                else from_state
            ),
            to_state=(
                to_state.value
                if hasattr(to_state, "value")
                else to_state
            ),
        )

    def record_authentication(
        self,
        call_id: str,
    ) -> CallEvent:
        event = CallEvent(
            call_id=call_id,
            event_type="AUTHENTICATION",
            from_state="AUTHENTICATION",
            to_state="DISCLOSE_OVERDUE",
        )

        return self.repository.create(event)

    def record_authentication_failed(
        self,
        call_id: str,
    ) -> CallEvent:
        event = CallEvent(
            call_id=call_id,
            event_type="AUTHENTICATION_FAILED",
            from_state="AUTHENTICATION",
            to_state="END",
        )

        return self.repository.create(event)

    def record_verification_success(
        self,
        call_id: str,
    ) -> CallEvent:
        event = CallEvent(
            call_id=call_id,
            event_type="VERIFICATION_SUCCESS",
            from_state="AUTHENTICATION",
            to_state="DISCLOSE_OVERDUE",
        )

        return self.repository.create(event)

    def record_verification_failed(
        self,
        call_id: str,
        to_state: str,
    ) -> CallEvent:
        event = CallEvent(
            call_id=call_id,
            event_type="VERIFICATION_FAILED",
            from_state="AUTHENTICATION",
            to_state=to_state,
        )

        return self.repository.create(event)

    def get_call_events(
        self,
        call_id: str,
    ) -> list[CallEvent]:
        return self.repository.get_by_call_id(
            call_id
        )

    def record_call_ended(
        self,
        call_id: str,
    ) -> CallEvent:
        event = CallEvent(
            call_id=call_id,
            event_type="CALL_ENDED",
            from_state=None,
            to_state="END",
        )

        result = self.repository.create(event)

        VOICE_CALLS_ENDED_TOTAL.inc()

        return result
