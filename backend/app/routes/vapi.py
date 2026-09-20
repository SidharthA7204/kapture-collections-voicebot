from fastapi import APIRouter, Depends, Header, HTTPException
import secrets
import structlog

from app.api.dependencies import get_vapi_webhook_service
from app.core.config import settings
from app.core.logging import logger
from app.schemas.vapi import (
    VapiWebhookRequest,
    VapiWebhookResponse,
)
from app.services.vapi_webhook_service import VapiWebhookService


router = APIRouter(
    prefix="/vapi",
    tags=["vapi"],
)


def verify_vapi_webhook(
    authorization: str | None,
) -> None:
    if not settings.VAPI_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=503,
            detail=(
                "Vapi webhook authentication "
                "is not configured."
            ),
        )

    expected = f"Bearer {settings.VAPI_WEBHOOK_SECRET}"

    if not authorization or not secrets.compare_digest(
        authorization,
        expected,
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )


@router.post(
    "/webhook",
    response_model=VapiWebhookResponse,
    response_model_exclude_none=True,
)
def vapi_webhook(
    request: VapiWebhookRequest,
    authorization: str | None = Header(
        default=None,
    ),
    service: VapiWebhookService = Depends(
        get_vapi_webhook_service
    ),
):
    verify_vapi_webhook(authorization)

    if request.message.call is None:
        raise HTTPException(
            status_code=422,
            detail="Call information is required.",
        )

    call_id = request.message.call.id
    status = request.message.call.status
    event_type = request.message.type
    event_id = request.message.id
    structlog.contextvars.bind_contextvars(
        call_id=call_id,
    )

    logger.info(
        "vapi_webhook_received",
        event_type=event_type,
        call_status=status,
        event_id=event_id,
    )

    if event_id and service.is_duplicate_event(event_id):
        logger.info(
            "vapi_webhook_duplicate",
            event_type=event_type,
            event_id=event_id,
        )

        return VapiWebhookResponse(
            status="duplicate",
            event_type=event_type,
            call_id=call_id,
        )

    if event_type == "status-update":
        session = service.handle_status_update(
            call_id=call_id,
            status=status,
        )

        return VapiWebhookResponse(
            status="ok",
            event_type=event_type,
            call_id=session.call_id,
        )

    if event_type == "end-of-call-report":
        session = service.handle_ended_call_by_call_id(
            call_id=call_id,
        )

        return VapiWebhookResponse(
            status="ok",
            event_type=event_type,
            call_id=session.call_id,
        )

    if event_type == "action-request":
        if not request.message.content:
            return VapiWebhookResponse(
                status="ok",
                event_type=event_type,
                call_id=call_id,
            )

        result = service.handle_ai_action(
            call_id=call_id,
            user_message=request.message.content,
        )

        service.mark_event_processed(
            event_id=event_id,
            event_type=event_type,
            call_id=call_id,
        )

        return VapiWebhookResponse(
            status="ok",
            event_type=event_type,
            call_id=call_id,
            response=str(result),
        )
    if event_type == "assistant-request":
        if not request.message.content:
            return VapiWebhookResponse(
                status="ok",
                event_type=event_type,
                call_id=call_id,
            )

        response = service.handle_assistant_request(
            call_id=call_id,
            user_message=request.message.content,
            current_state=status,
        )

        return VapiWebhookResponse(
            status="ok",
            event_type=event_type,
            call_id=call_id,
            response=response,
        )

    return VapiWebhookResponse(
        status="ok",
        event_type=event_type,
        call_id=call_id,
    )













