from fastapi import APIRouter, Depends, HTTPException, HTTPException

from app.api.dependencies import (
    get_ai_action_service,
    get_ai_conversation_service,
    get_ai_intent_service,
    get_call_flow_service,
    get_conversation_extraction_service,
)
from app.schemas.ai import (
    AIAnalyzeRequest,
    AIAnalyzeResponse,
    AIChatRequest,
    AIChatResponse,
    AIExecuteRequest,
    AIExecuteResponse,
    AIExtractionRequest,
    AIExtractionResponse,
)
from app.services.ai_action_service import AIActionService
from app.services.ai_conversation_service import (
    AIConversationService,
)
from app.services.ai_intent_service import AIIntentService
from app.services.call_flow_service import CallFlowService
from app.state.states import CallState
from app.state.states import CallState
from app.services.conversation_extraction_service import (
    ConversationExtractionService,
)


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)


@router.post(
    "/chat",
    response_model=AIChatResponse,
)
def ai_chat(
    request: AIChatRequest,
    service: AIConversationService = Depends(
        get_ai_conversation_service
    ),
):
    response = service.generate_response(
        user_message=request.message,
        current_state=request.current_state,
    )

    return AIChatResponse(
        response=response,
    )


@router.post(
    "/extract",
    response_model=AIExtractionResponse,
)
def ai_extract(
    request: AIExtractionRequest,
    service: ConversationExtractionService = Depends(
        get_conversation_extraction_service
    ),
):
    extraction = service.extract(
        user_message=request.message
    )

    return AIExtractionResponse(
        extraction=extraction,
    )


@router.post(
    "/analyze",
    response_model=AIAnalyzeResponse,
)
def ai_analyze(
    request: AIAnalyzeRequest,
    extraction_service: ConversationExtractionService = Depends(
        get_conversation_extraction_service
    ),
    intent_service: AIIntentService = Depends(
        get_ai_intent_service
    ),
):
    extraction = extraction_service.extract(
        user_message=request.message
    )

    action = intent_service.determine_action(
        extraction
    )

    return AIAnalyzeResponse(
        extraction=extraction,
        action=action,
    )


@router.post(
    "/execute",
    response_model=AIExecuteResponse,
)
def ai_execute(
    request: AIExecuteRequest,
    extraction_service: ConversationExtractionService = Depends(
        get_conversation_extraction_service
    ),
    ai_action_service: AIActionService = Depends(
        get_ai_action_service
    ),
    call_flow_service: CallFlowService = Depends(
        get_call_flow_service
    ),
):
    extraction = extraction_service.extract(
        user_message=request.message
    )

    machine = call_flow_service.restore_machine(
        request.call_id
    )

    if machine.current_state in (
        CallState.DISPOSITION,
        CallState.END,
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Call has already completed action execution."
            ),
        )

    action = ai_action_service.intent_service.determine_action(
        extraction
    )

    disposition = ai_action_service.execute(
        call_id=request.call_id,
        customer_id=request.customer_id,
        loan_id=request.loan_id,
        machine=machine,
        extraction=extraction,
    )

    call_flow_service.end_call(
        call_id=request.call_id,
        machine=machine,
    )

    return AIExecuteResponse(
        call_id=request.call_id,
        extraction=extraction,
        action=action,
        disposition=disposition.value,
    )




