from app.services.ai_action_service import AIActionService
from app.services.ai_conversation_service import AIConversationService
from app.services.call_flow_service import CallFlowService
from app.services.conversation_extraction_service import (
    ConversationExtractionService,
)
from app.services.loan_service import LoanService
from app.services.webhook_event_service import WebhookEventService
from app.state.states import CallState


class VapiWebhookService:

    def __init__(
        self,
        call_flow_service: CallFlowService,
        ai_conversation_service: AIConversationService | None = None,
        conversation_extraction_service: (
            ConversationExtractionService | None
        ) = None,
        ai_action_service: AIActionService | None = None,
        loan_service: LoanService | None = None,
        webhook_event_service: WebhookEventService | None = None,
    ):
        self.call_flow_service = call_flow_service
        self.ai_conversation_service = ai_conversation_service
        self.conversation_extraction_service = (
            conversation_extraction_service
        )
        self.ai_action_service = ai_action_service
        self.loan_service = loan_service
        self.webhook_event_service = webhook_event_service

    def is_duplicate_event(
        self,
        event_id: str | None,
    ) -> bool:
        if not event_id:
            return False

        if self.webhook_event_service is None:
            return False

        return self.webhook_event_service.already_processed(
            provider="vapi",
            event_id=event_id,
        )

    def mark_event_processed(
        self,
        event_id: str | None,
        event_type: str,
        call_id: str,
    ) -> None:
        if not event_id:
            return

        if self.webhook_event_service is None:
            return

        self.webhook_event_service.mark_processed(
            provider="vapi",
            event_id=event_id,
            event_type=event_type,
            call_id=call_id,
        )
    def handle_status_update(
        self,
        call_id: str,
        status: str | None = None,
    ):
        session = (
            self.call_flow_service
            .session_service
            .get_session(call_id)
        )

        if session is None:
            _, session, _ = (
                self.call_flow_service.start_call(
                    call_id=call_id,
                    customer_id=None,
                )
            )

        if status == "ended":
            return self.handle_ended_call(
                call_id=call_id,
                session=session,
            )

        return session

    def handle_assistant_request(
        self,
        call_id: str,
        user_message: str,
        current_state: str | None = None,
    ) -> str:
        if not user_message.strip():
            raise ValueError(
                "Assistant request message cannot be empty."
            )

        if self.ai_conversation_service is None:
            raise RuntimeError(
                "AI conversation service is not configured."
            )

        session = (
            self.call_flow_service
            .session_service
            .get_session(call_id)
        )

        if session is None:
            _, session, _ = (
                self.call_flow_service.start_call(
                    call_id=call_id,
                    customer_id=None,
                )
            )

        if session.current_state in (
            CallState.END.value,
        ):
            raise ValueError(
                "Cannot process conversation for an ended call."
            )

        state = session.current_state

        return self.ai_conversation_service.generate_response(
            user_message=user_message,
            current_state=state,
        )

    def handle_ai_action(
        self,
        call_id: str,
        user_message: str,
    ):
        if not user_message.strip():
            raise ValueError(
                "Assistant request message cannot be empty."
            )

        if self.conversation_extraction_service is None:
            raise RuntimeError(
                "Conversation extraction service is not configured."
            )

        if self.ai_action_service is None:
            raise RuntimeError(
                "AI action service is not configured."
            )

        if self.loan_service is None:
            raise RuntimeError(
                "Loan service is not configured."
            )

        session = (
            self.call_flow_service
            .session_service
            .get_session(call_id)
        )

        if session is None:
            raise ValueError(
                f"Call session not found: {call_id}"
            )

        if session.current_state in (
            CallState.END.value,
        ):
            raise ValueError(
                "Cannot process conversation for an ended call."
            )

        extraction = (
            self.conversation_extraction_service.extract(
                user_message=user_message,
            )
        )

        customer_id = session.customer_id
        loan_id = None

        if customer_id is not None:
            loans = self.loan_service.get_customer_loans(
                customer_id
            )

            if len(loans) == 1:
                loan_id = loans[0].id

            elif (
                extraction.intent.value == "PROMISE_TO_PAY"
                and len(loans) != 1
            ):
                raise ValueError(
                    "Unable to determine a unique loan "
                    "for this customer."
                )

        machine = self.call_flow_service.restore_machine(
            call_id
        )

        result = self.ai_action_service.execute(
            call_id=call_id,
            customer_id=customer_id,
            loan_id=loan_id,
            machine=machine,
            extraction=extraction,
        )

        return {
            "extraction": extraction,
            "result": result,
        }

    def handle_ended_call_by_call_id(
        self,
        call_id: str,
    ):
        session = (
            self.call_flow_service
            .session_service
            .get_session(call_id)
        )

        if session is None:
            _, session, _ = (
                self.call_flow_service.start_call(
                    call_id=call_id,
                    customer_id=None,
                )
            )

        return self.handle_ended_call(
            call_id=call_id,
            session=session,
        )

    def handle_ended_call(
        self,
        call_id: str,
        session,
    ):
        if session.current_state != CallState.END.value:
            session = (
                self.call_flow_service
                .session_service
                .update_state(
                    call_id=call_id,
                    state=CallState.END,
                )
            )

            self.call_flow_service.call_event_service.record_call_ended(
                call_id=call_id,
            )

            self.call_flow_service.call_log_service.end_call(
                call_id=call_id,
            )

        return session


