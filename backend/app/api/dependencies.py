from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.transaction import transaction
from app.db.repositories.call_event_repository import CallEventRepository
from app.db.repositories.call_log_repository import CallLogRepository
from app.db.repositories.customer_repository import CustomerRepository
from app.db.repositories.dispute_repository import DisputeRepository
from app.db.repositories.promise_to_pay_repository import PromiseToPayRepository
from app.db.repositories.session_repository import SessionRepository
from app.db.repositories.webhook_event_repository import WebhookEventRepository

from app.services.ai_action_service import AIActionService
from app.services.ai_intent_service import AIIntentService
from app.services.assistance_service import AssistanceService
from app.services.call_event_service import CallEventService
from app.services.call_flow_service import CallFlowService
from app.services.call_log_service import CallLogService
from app.services.collections_intent_service import CollectionsIntentService
from app.services.customer_service import CustomerService
from app.services.customer_verification_service import CustomerVerificationService
from app.services.dispute_service import DisputeService
from app.services.disposition_service import DispositionService
from app.services.intent_service import IntentService
from app.services.payment_service import PaymentService
from app.services.promise_to_pay_service import PromiseToPayService
from app.services.loan_service import LoanService
from app.db.repositories.loan_repository import LoanRepository
from app.services.session_service import SessionService
from app.services.conversation_extraction_service import ConversationExtractionService
from app.services.groq_service import GroqService
from app.services.webhook_event_service import WebhookEventService


def get_groq_service() -> GroqService:
    return GroqService()


def get_call_flow_service(
    db: Session = Depends(get_db),
) -> CallFlowService:

    session_service = SessionService(
        SessionRepository(db)
    )

    call_log_service = CallLogService(
        CallLogRepository(db)
    )

    call_event_service = CallEventService(
        CallEventRepository(db)
    )

    collections_intent_service = CollectionsIntentService(
        intent_service=IntentService(),
        dispute_service=DisputeService(
            DisputeRepository(db)
        ),
        promise_to_pay_service=PromiseToPayService(
            PromiseToPayRepository(db)
        ),
        payment_service=PaymentService(),
        assistance_service=AssistanceService(),
        disposition_service=DispositionService(),
        call_log_service=call_log_service,
    )

    customer_service = CustomerService(
        CustomerRepository(db)
    )

    customer_verification_service = CustomerVerificationService()

    return CallFlowService(
        session_service=session_service,
        call_log_service=call_log_service,
        collections_intent_service=collections_intent_service,
        customer_service=customer_service,
        customer_verification_service=customer_verification_service,
        call_event_service=call_event_service,
        transaction_manager=lambda: transaction(db),
    )


def get_call_event_service(
    db: Session = Depends(get_db),
) -> CallEventService:
    return CallEventService(
        CallEventRepository(db)
    )


def get_ai_conversation_service():
    from app.services.ai_conversation_service import AIConversationService

    return AIConversationService(
        groq_service=get_groq_service()
    )


def get_conversation_extraction_service():
    return ConversationExtractionService(
        groq_service=get_groq_service()
    )


def get_ai_intent_service() -> AIIntentService:
    return AIIntentService(
        intent_service=IntentService()
    )


def get_ai_action_service(
    call_flow_service: CallFlowService = Depends(
        get_call_flow_service
    ),
    ai_intent_service: AIIntentService = Depends(
        get_ai_intent_service
    ),
) -> AIActionService:

    return AIActionService(
        intent_service=ai_intent_service,
        call_flow_service=call_flow_service,
    )


def get_webhook_event_service(
    db: Session = Depends(get_db),
) -> WebhookEventService:
    return WebhookEventService(
        WebhookEventRepository(db)
    )


def get_vapi_webhook_service(
    call_flow_service: CallFlowService = Depends(
        get_call_flow_service
    ),
    ai_conversation_service = Depends(
        get_ai_conversation_service
    ),
    conversation_extraction_service: ConversationExtractionService = Depends(
        get_conversation_extraction_service
    ),
    ai_action_service: AIActionService = Depends(
        get_ai_action_service
    ),
    webhook_event_service: WebhookEventService = Depends(
        get_webhook_event_service
    ),
    db: Session = Depends(get_db),
):
    from app.services.vapi_webhook_service import VapiWebhookService

    loan_service = LoanService(
        LoanRepository(db)
    )

    return VapiWebhookService(
        call_flow_service=call_flow_service,
        ai_conversation_service=ai_conversation_service,
        conversation_extraction_service=conversation_extraction_service,
        ai_action_service=ai_action_service,
        loan_service=loan_service,
        webhook_event_service=webhook_event_service,
    )
