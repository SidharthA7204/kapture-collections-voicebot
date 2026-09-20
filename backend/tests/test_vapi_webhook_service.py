from unittest.mock import Mock

from app.services.vapi_webhook_service import (
    VapiWebhookService,
)
from app.state.states import CallState


def create_service():
    call_flow_service = Mock()

    call_flow_service.session_service = Mock()
    call_flow_service.call_event_service = Mock()
    call_flow_service.call_log_service = Mock()

    return (
        VapiWebhookService(
            call_flow_service=call_flow_service,
        ),
        call_flow_service,
    )


def test_status_update_returns_existing_session():
    service, call_flow_service = create_service()

    session = Mock()
    session.call_id = "call-001"
    session.current_state = "INTENT_HANDLING"

    call_flow_service.session_service.get_session.return_value = (
        session
    )

    result = service.handle_status_update(
        call_id="call-001",
        status="in-progress",
    )

    assert result is session

    call_flow_service.session_service.get_session.assert_called_once_with(
        "call-001"
    )

    call_flow_service.start_call.assert_not_called()


def test_status_update_creates_session_when_missing():
    service, call_flow_service = create_service()

    new_session = Mock()
    new_session.call_id = "call-002"

    call_flow_service.session_service.get_session.return_value = None

    call_flow_service.start_call.return_value = (
        Mock(),
        new_session,
        Mock(),
    )

    result = service.handle_status_update(
        call_id="call-002",
        status="in-progress",
    )

    assert result is new_session

    call_flow_service.start_call.assert_called_once_with(
        call_id="call-002",
        customer_id=None,
    )


def test_ended_status_ends_call():
    service, call_flow_service = create_service()

    session = Mock()
    session.call_id = "call-003"
    session.current_state = "INTENT_HANDLING"

    call_flow_service.session_service.get_session.return_value = (
        session
    )

    ended_session = Mock()
    ended_session.call_id = "call-003"
    ended_session.current_state = CallState.END.value

    call_flow_service.session_service.update_state.return_value = (
        ended_session
    )

    result = service.handle_status_update(
        call_id="call-003",
        status="ended",
    )

    assert result is ended_session

    call_flow_service.session_service.update_state.assert_called_once_with(
        call_id="call-003",
        state=CallState.END,
    )

    call_flow_service.call_event_service.record_call_ended.assert_called_once_with(
        call_id="call-003",
    )

    call_flow_service.call_log_service.end_call.assert_called_once_with(
        call_id="call-003",
    )


def test_handle_ended_call_does_not_repeat_end_operations():
    service, call_flow_service = create_service()

    session = Mock()
    session.call_id = "call-004"
    session.current_state = CallState.END.value

    result = service.handle_ended_call(
        call_id="call-004",
        session=session,
    )

    assert result is session

    call_flow_service.session_service.update_state.assert_not_called()

    call_flow_service.call_event_service.record_call_ended.assert_not_called()

    call_flow_service.call_log_service.end_call.assert_not_called()


def test_handle_ended_call_updates_active_session():
    service, call_flow_service = create_service()

    session = Mock()
    session.call_id = "call-005"
    session.current_state = "PAYMENT_COMMITMENT"

    ended_session = Mock()
    ended_session.call_id = "call-005"
    ended_session.current_state = CallState.END.value

    call_flow_service.session_service.update_state.return_value = (
        ended_session
    )

    result = service.handle_ended_call(
        call_id="call-005",
        session=session,
    )

    assert result is ended_session

    call_flow_service.session_service.update_state.assert_called_once_with(
        call_id="call-005",
        state=CallState.END,
    )

    call_flow_service.call_event_service.record_call_ended.assert_called_once_with(
        call_id="call-005",
    )

    call_flow_service.call_log_service.end_call.assert_called_once_with(
        call_id="call-005",
    )

def test_handle_assistant_request_uses_existing_session(
    db_session,
    monkeypatch,
):
    from app.services.call_flow_service import CallFlowService
    from app.services.vapi_webhook_service import VapiWebhookService
    from tests.test_call_flow_service import create_service

    call_flow_service = create_service(db_session)

    call_id = "assistant-service-existing-001"

    call_flow_service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    class FakeAIConversationService:
        def generate_response(
            self,
            user_message,
            current_state=None,
        ):
            assert user_message == "I want to make a payment."
            assert current_state == "CALL_CONNECTED"
            return "How much would you like to pay?"

    service = VapiWebhookService(
        call_flow_service=call_flow_service,
        ai_conversation_service=FakeAIConversationService(),
    )

    response = service.handle_assistant_request(
        call_id=call_id,
        user_message="I want to make a payment.",
    )

    assert response == "How much would you like to pay?"


def test_handle_assistant_request_creates_missing_session(
    db_session,
):
    from app.services.vapi_webhook_service import VapiWebhookService
    from tests.test_call_flow_service import create_service

    call_flow_service = create_service(db_session)

    class FakeAIConversationService:
        def generate_response(
            self,
            user_message,
            current_state=None,
        ):
            assert user_message == "Hello"
            assert current_state == "CALL_CONNECTED"
            return "Hello, how can I help you?"

    service = VapiWebhookService(
        call_flow_service=call_flow_service,
        ai_conversation_service=FakeAIConversationService(),
    )

    call_id = "assistant-service-create-001"

    response = service.handle_assistant_request(
        call_id=call_id,
        user_message="Hello",
    )

    assert response == "Hello, how can I help you?"

    session = (
        call_flow_service.session_service
        .get_session(call_id)
    )

    assert session is not None
    assert session.current_state == "CALL_CONNECTED"


def test_handle_assistant_request_rejects_ended_call(
    db_session,
):
    import pytest

    from app.state.states import CallState
    from app.services.vapi_webhook_service import (
        VapiWebhookService,
    )
    from tests.test_call_flow_service import create_service

    call_flow_service = create_service(db_session)

    call_id = "assistant-service-ended-001"

    call_flow_service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    machine = call_flow_service.restore_machine(call_id)

    call_flow_service.transition(
        call_id=call_id,
        machine=machine,
        next_state=CallState.INTRODUCTION,
    )

    call_flow_service.transition(
        call_id=call_id,
        machine=machine,
        next_state=CallState.CHECK_PERSON,
    )

    call_flow_service.transition(
        call_id=call_id,
        machine=machine,
        next_state=CallState.END,
    )

    class FakeAIConversationService:
        def generate_response(
            self,
            user_message,
            current_state=None,
        ):
            raise AssertionError(
                "AI service should not be called for ended calls."
            )

    service = VapiWebhookService(
        call_flow_service=call_flow_service,
        ai_conversation_service=FakeAIConversationService(),
    )

    with pytest.raises(
        ValueError,
        match="ended call",
    ):
        service.handle_assistant_request(
            call_id=call_id,
            user_message="Hello",
        )


def test_handle_assistant_request_rejects_empty_message(
    db_session,
):
    import pytest

    from app.services.vapi_webhook_service import (
        VapiWebhookService,
    )
    from tests.test_call_flow_service import create_service

    call_flow_service = create_service(db_session)

    class FakeAIConversationService:
        def generate_response(
            self,
            user_message,
            current_state=None,
        ):
            raise AssertionError(
                "AI service should not be called."
            )

    service = VapiWebhookService(
        call_flow_service=call_flow_service,
        ai_conversation_service=FakeAIConversationService(),
    )

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        service.handle_assistant_request(
            call_id="assistant-service-empty-001",
            user_message="   ",
        )


def test_handle_assistant_request_uses_current_call_state(
    db_session,
):
    from app.services.vapi_webhook_service import (
        VapiWebhookService,
    )
    from app.state.states import CallState
    from tests.test_call_flow_service import create_service

    call_flow_service = create_service(db_session)

    call_id = "assistant-state-aware-001"

    call_flow_service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    machine = call_flow_service.restore_machine(call_id)

    for next_state in (
        CallState.INTRODUCTION,
        CallState.CHECK_PERSON,
        CallState.AUTHENTICATION,
        CallState.DISCLOSE_OVERDUE,
        CallState.INTENT_HANDLING,
    ):
        call_flow_service.transition(
            call_id=call_id,
            machine=machine,
            next_state=next_state,
        )

    class FakeAIConversationService:
        def generate_response(
            self,
            user_message,
            current_state=None,
        ):
            assert user_message == "I cannot pay today."
            assert current_state == CallState.INTENT_HANDLING.value

            return (
                "I understand. Would you like to provide "
                "a date when you can make the payment?"
            )

    service = VapiWebhookService(
        call_flow_service=call_flow_service,
        ai_conversation_service=FakeAIConversationService(),
    )

    response = service.handle_assistant_request(
        call_id=call_id,
        user_message="I cannot pay today.",
    )

    assert response == (
        "I understand. Would you like to provide "
        "a date when you can make the payment?"
    )


def test_handle_assistant_request_preserves_state_when_ai_fails(
    db_session,
):
    import pytest

    from app.services.vapi_webhook_service import (
        VapiWebhookService,
    )
    from app.state.states import CallState
    from tests.test_call_flow_service import create_service

    call_flow_service = create_service(db_session)

    call_id = "assistant-ai-failure-001"

    call_flow_service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    machine = call_flow_service.restore_machine(call_id)

    for next_state in (
        CallState.INTRODUCTION,
        CallState.CHECK_PERSON,
        CallState.AUTHENTICATION,
        CallState.DISCLOSE_OVERDUE,
        CallState.INTENT_HANDLING,
    ):
        call_flow_service.transition(
            call_id=call_id,
            machine=machine,
            next_state=next_state,
        )

    class FailingAIConversationService:
        def generate_response(
            self,
            user_message,
            current_state=None,
        ):
            raise RuntimeError(
                "AI provider temporarily unavailable."
            )

    service = VapiWebhookService(
        call_flow_service=call_flow_service,
        ai_conversation_service=FailingAIConversationService(),
    )

    with pytest.raises(
        RuntimeError,
        match="AI provider temporarily unavailable",
    ):
        service.handle_assistant_request(
            call_id=call_id,
            user_message="I need help with my payment.",
        )

    session = (
        call_flow_service.session_service
        .get_session(call_id)
    )

    assert session is not None
    assert session.current_state == (
        CallState.INTENT_HANDLING.value
    )


def test_handle_assistant_request_preserves_state_when_ai_fails(
    db_session,
):
    import pytest

    from app.services.vapi_webhook_service import (
        VapiWebhookService,
    )
    from app.state.states import CallState
    from tests.test_call_flow_service import create_service

    call_flow_service = create_service(db_session)

    call_id = "assistant-ai-failure-001"

    call_flow_service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    machine = call_flow_service.restore_machine(call_id)

    for next_state in (
        CallState.INTRODUCTION,
        CallState.CHECK_PERSON,
        CallState.AUTHENTICATION,
        CallState.DISCLOSE_OVERDUE,
        CallState.INTENT_HANDLING,
    ):
        call_flow_service.transition(
            call_id=call_id,
            machine=machine,
            next_state=next_state,
        )

    class FailingAIConversationService:
        def generate_response(
            self,
            user_message,
            current_state=None,
        ):
            raise RuntimeError(
                "AI provider temporarily unavailable."
            )

    service = VapiWebhookService(
        call_flow_service=call_flow_service,
        ai_conversation_service=FailingAIConversationService(),
    )

    with pytest.raises(
        RuntimeError,
        match="AI provider temporarily unavailable",
    ):
        service.handle_assistant_request(
            call_id=call_id,
            user_message="I need help with my payment.",
        )

    session = (
        call_flow_service.session_service
        .get_session(call_id)
    )

    assert session is not None
    assert session.current_state == (
        CallState.INTENT_HANDLING.value
    )

