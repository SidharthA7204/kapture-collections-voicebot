from datetime import date

from app.schemas.intent_action import IntentAction
from app.services.call_log_service import CallLogService
from app.services.collections_intent_service import (
    CollectionsIntentService,
)
from app.services.session_service import SessionService
from app.services.customer_service import CustomerService
from app.services.customer_verification_service import (
    CustomerVerificationService,
)
from app.services.call_event_service import CallEventService
from app.state.state_machine import (
    CallStateMachine,
    InvalidStateTransition,
)
from app.state.states import CallState


class CallFlowService:

    MAX_VERIFICATION_ATTEMPTS = 3

    def __init__(
        self,
        session_service: SessionService,
        call_log_service: CallLogService,
        collections_intent_service: CollectionsIntentService,
        customer_service: CustomerService | None = None,
        customer_verification_service: (
            CustomerVerificationService | None
        ) = None,
        call_event_service: CallEventService | None = None,
        transaction_manager=None,
    ):
        self.session_service = session_service
        self.call_log_service = call_log_service
        self.collections_intent_service = (
            collections_intent_service
        )
        self.customer_service = customer_service
        self.customer_verification_service = (
            customer_verification_service
        )
        self.call_event_service = call_event_service

        if transaction_manager is not None:
            self.transaction_manager = transaction_manager
        else:
            from app.db.transaction import transaction

            self.transaction_manager = lambda: transaction(
                self.session_service.repository.db
            )

    def start_call(
        self,
        call_id: str,
        customer_id: int | None = None,
    ):
        machine = CallStateMachine()

        existing_session = (
            self.session_service.get_session(call_id)
        )

        if existing_session is not None:
            if (
                customer_id is not None
                and existing_session.customer_id is not None
                and existing_session.customer_id != customer_id
            ):
                from fastapi import HTTPException

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Call ID is already associated "
                        "with a different customer."
                    ),
                )

            call_log = (
                self.call_log_service.repository
                .get_by_call_id(call_id)
            )

            return (
                machine,
                existing_session,
                call_log,
            )

        session = self.session_service.create_session(
            call_id=call_id,
            customer_id=customer_id,
        )

        call_log = self.call_log_service.start_call(
            call_id=call_id,
            customer_id=customer_id,
        )

        return (
            machine,
            session,
            call_log,
        )

    def transition(
        self,
        call_id: str,
        machine: CallStateMachine,
        next_state: CallState,
        commit: bool = True,
    ):
        previous_state = machine.current_state

        state = machine.transition(next_state)

        session = self.session_service.update_state(
            call_id=call_id,
            state=state,
            commit=commit,
        )

        if self.call_event_service is not None:
            self.call_event_service.record_state_change(
                call_id=call_id,
                from_state=previous_state.value,
                to_state=state.value,
                commit=commit,
            )

        return session

    def authenticate(
        self,
        call_id: str,
        machine: CallStateMachine,
    ):
        if machine.current_state != CallState.AUTHENTICATION:
            raise InvalidStateTransition(
                "Authentication is only allowed "
                "during AUTHENTICATION"
            )

        session = self.session_service.authenticate(
            call_id
        )

        if self.call_event_service is not None:
            self.call_event_service.record_authentication(
                call_id=call_id,
            )

        self.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.DISCLOSE_OVERDUE,
        )

        return session

    def verify_customer(
        self,
        call_id: str,
        machine: CallStateMachine,
        phone: str,
        dob: date,
    ):
        if machine.current_state != CallState.AUTHENTICATION:
            raise InvalidStateTransition(
                "Customer verification is only allowed "
                "during AUTHENTICATION"
            )

        if self.customer_service is None:
            raise RuntimeError(
                "CustomerService is not configured"
            )

        if self.customer_verification_service is None:
            raise RuntimeError(
                "CustomerVerificationService is not configured"
            )

        session = self.session_service.get_session(
            call_id
        )

        if session is None:
            raise ValueError(
                f"Session not found: {call_id}"
            )

        if (
            session.verification_attempts
            >= self.MAX_VERIFICATION_ATTEMPTS
        ):
            self.person_not_verified(
                call_id=call_id,
                machine=machine,
            )

            return {
                "authenticated": False,
                "current_state": machine.current_state.value,
            }

        if session.customer_id is None:
            self.session_service.increment_verification_attempts(
                call_id
            )

            session = self.session_service.get_session(
                call_id
            )

            if (
                session.verification_attempts
                >= self.MAX_VERIFICATION_ATTEMPTS
            ):
                self.person_not_verified(
                    call_id=call_id,
                    machine=machine,
                )

            return {
                "authenticated": False,
                "current_state": machine.current_state.value,
            }

        customer = (
            self.customer_service.get_customer_by_id(
                session.customer_id
            )
        )

        verified = (
            self.customer_verification_service.verify(
                customer=customer,
                phone=phone,
                dob=dob,
            )
        )

        if verified:
            session = self.session_service.authenticate(
                call_id
            )

            if self.call_event_service is not None:
                self.call_event_service.record_verification_success(
                    call_id=call_id,
                )

            self.transition(
                call_id=call_id,
                machine=machine,
                next_state=CallState.DISCLOSE_OVERDUE,
            )

            return {
                "authenticated": session.authenticated,
                "current_state": machine.current_state.value,
            }

        self.session_service.increment_verification_attempts(
            call_id
        )

        session = self.session_service.get_session(
            call_id
        )

        if (
            session.verification_attempts
            >= self.MAX_VERIFICATION_ATTEMPTS
        ):
            if self.call_event_service is not None:
                self.call_event_service.record_verification_failed(
                    call_id=call_id,
                    to_state=CallState.END.value,
                )

            self.person_not_verified(
                call_id=call_id,
                machine=machine,
            )
        else:
            if self.call_event_service is not None:
                self.call_event_service.record_verification_failed(
                    call_id=call_id,
                    to_state=CallState.AUTHENTICATION.value,
                )

        return {
            "authenticated": False,
            "current_state": machine.current_state.value,
        }

    def handle_action(
        self,
        call_id: str,
        machine: CallStateMachine,
        action: IntentAction,
        customer_id: int | None = None,
        loan_id: int | None = None,
        amount=None,
        promise_date: date | None = None,
        dispute_description: str | None = None,
    ):
        if action == IntentAction.PROMISE_TO_PAY:
            if customer_id is None:
                raise ValueError(
                    "Customer ID is required for a promise to pay."
                )

            if loan_id is None:
                raise ValueError(
                    "Loan ID is required for a promise to pay."
                )

            if amount is None:
                raise ValueError(
                    "Promise amount is required."
                )

            if promise_date is None:
                raise ValueError(
                    "Promise date is required."
                )

            if self.transaction_manager is None:
                raise RuntimeError(
                    "Transaction manager is not configured."
                )

            with self.transaction_manager():
                self.collections_intent_service.create_promise(
                    customer_id=customer_id,
                    loan_id=loan_id,
                    amount=amount,
                    promise_date=promise_date,
                    commit=False,
                )

                disposition = (
                    self.collections_intent_service
                    .determine_disposition(action)
                )

                self.call_log_service.record_disposition(
                    call_id=call_id,
                    disposition=disposition.value,
                    commit=False,
                )

                self.transition(
                    call_id=call_id,
                    machine=machine,
                    next_state=CallState.DISPOSITION,
                    commit=False,
                )

                return disposition

        if action == IntentAction.DISPUTE:
            if customer_id is None:
                raise ValueError(
                    "Customer ID is required for a dispute."
                )

            if self.transaction_manager is None:
                raise RuntimeError(
                    "Transaction manager is not configured."
                )

            with self.transaction_manager():
                self.collections_intent_service.create_dispute(
                    customer_id=customer_id,
                    loan_id=loan_id,
                    reason="CUSTOMER_DISPUTE",
                    description=(
                        dispute_description
                        or "Customer disputed the overdue charge."
                    ),
                )

                disposition = (
                    self.collections_intent_service
                    .determine_disposition(action)
                )

                self.call_log_service.record_disposition(
                    call_id=call_id,
                    disposition=disposition.value,
                    commit=False,
                )

                self.transition(
                    call_id=call_id,
                    machine=machine,
                    next_state=CallState.DISPOSITION,
                    commit=False,
                )

                return disposition

        disposition = (
            self.collections_intent_service
            .determine_disposition(action)
        )

        self.call_log_service.record_disposition(
            call_id=call_id,
            disposition=disposition.value,
        )

        self.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.DISPOSITION,
        )

        return disposition

    def end_call(
        self,
        call_id: str,
        machine: CallStateMachine,
    ):
        if machine.current_state == CallState.END:
            return self.session_service.get_session(
                call_id
            )

        self.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.END,
        )

        if self.call_event_service is not None:
            self.call_event_service.record_call_ended(
                call_id=call_id,
            )

        return self.call_log_service.end_call(
            call_id
        )

    def authentication_failed(
        self,
        call_id: str,
        machine: CallStateMachine,
    ):
        if self.call_event_service is not None:
            self.call_event_service.record_authentication_failed(
                call_id=call_id,
            )

        session = self.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.END,
        )

        if self.call_event_service is not None:
            self.call_event_service.record_call_ended(
                call_id=call_id,
            )

        self.call_log_service.end_call(
            call_id
        )

        return session

    def person_not_verified(
        self,
        call_id: str,
        machine: CallStateMachine,
    ):
        session = self.transition(
            call_id=call_id,
            machine=machine,
            next_state=CallState.END,
        )

        if self.call_event_service is not None:
            self.call_event_service.record_call_ended(
                call_id=call_id,
            )

        self.call_log_service.end_call(
            call_id
        )

        return session

    def restore_machine(
        self,
        call_id: str,
    ) -> CallStateMachine:
        session = self.session_service.get_session(
            call_id
        )

        if session is None:
            raise ValueError(
                f"Session not found: {call_id}"
            )

        machine = CallStateMachine()

        machine.current_state = CallState(
            session.current_state
        )

        return machine


