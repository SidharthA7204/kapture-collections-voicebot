from app.db.repositories.session_repository import SessionRepository
from app.models.session import Session
from app.state.states import CallState


class SessionService:

    def __init__(
        self,
        repository: SessionRepository,
    ):
        self.repository = repository

    def create_session(
        self,
        call_id: str,
        customer_id: int | None = None,
    ) -> Session:
        session = Session(
            call_id=call_id,
            customer_id=customer_id,
            authenticated=False,
            verification_attempts=0,
            current_state=CallState.CALL_CONNECTED.value,
        )

        return self.repository.create(session)

    def get_session(
        self,
        call_id: str,
    ) -> Session | None:
        return self.repository.get_by_call_id(call_id)

    def authenticate(
        self,
        call_id: str,
    ) -> Session:
        session = self._get_required_session(call_id)

        session.authenticated = True

        return self.repository.update(session)

    def update_state(
        self,
        call_id: str,
        state: CallState,
        commit: bool = True,
    ) -> Session:
        session = self._get_required_session(call_id)

        session.current_state = state.value

        return self.repository.update(
            session,
            commit=commit,
        )

    def _get_required_session(
        self,
        call_id: str,
    ) -> Session:
        session = self.repository.get_by_call_id(call_id)

        if session is None:
            raise ValueError(
                f"Session not found: {call_id}"
            )

        return session

    def increment_verification_attempts(
        self,
        call_id: str,
    ) -> Session:
        session = self._get_required_session(call_id)

        session.verification_attempts += 1

        return self.repository.update(session)

    def get_verification_attempts(
        self,
        call_id: str,
    ) -> int:
        return self._get_required_session(
            call_id
        ).verification_attempts
