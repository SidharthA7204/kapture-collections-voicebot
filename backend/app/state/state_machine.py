from app.state.states import CallState


class InvalidStateTransition(Exception):
    pass


class CallStateMachine:

    TRANSITIONS = {
        CallState.CALL_CONNECTED: {
            CallState.INTRODUCTION,
        },
        CallState.INTRODUCTION: {
            CallState.CHECK_PERSON,
        },
        CallState.CHECK_PERSON: {
            CallState.AUTHENTICATION,
            CallState.END,
        },
        CallState.AUTHENTICATION: {
            CallState.DISCLOSE_OVERDUE,
            CallState.END,
        },
        CallState.DISCLOSE_OVERDUE: {
            CallState.INTENT_HANDLING,
        },
        CallState.INTENT_HANDLING: {
            CallState.DISPOSITION,
            CallState.END,
        },
        CallState.DISPOSITION: {
            CallState.END,
        },
        CallState.END: set(),
    }

    def __init__(self):
        self.current_state = CallState.CALL_CONNECTED

    def restore(
        self,
        state: CallState,
    ) -> CallState:
        self.current_state = state
        return self.current_state

    def transition(
        self,
        next_state: CallState,
    ) -> CallState:

        allowed_states = self.TRANSITIONS.get(
            self.current_state,
            set(),
        )

        if next_state not in allowed_states:
            raise InvalidStateTransition(
                f"Invalid transition: "
                f"{self.current_state} -> {next_state}"
            )

        self.current_state = next_state

        return self.current_state
