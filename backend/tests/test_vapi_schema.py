import pytest
from pydantic import ValidationError

from app.schemas.vapi import (
    VapiCall,
    VapiMessage,
    VapiWebhookRequest,
)


def test_vapi_status_update_is_accepted():
    payload = {
        "message": {
            "type": "status-update",
            "call": {
                "id": "vapi-call-001",
                "status": "in-progress",
            },
        }
    }

    request = VapiWebhookRequest.model_validate(payload)

    assert request.message.type == "status-update"
    assert request.message.call.id == "vapi-call-001"


def test_vapi_webhook_requires_message():
    with pytest.raises(ValidationError):
        VapiWebhookRequest.model_validate({})


def test_vapi_call_requires_id():
    with pytest.raises(ValidationError):
        VapiCall.model_validate({
            "status": "in-progress",
        })


def test_vapi_message_requires_type():
    with pytest.raises(ValidationError):
        VapiMessage.model_validate({
            "call": {
                "id": "vapi-call-001",
            }
        })

def test_vapi_status_update_requires_call():
    with pytest.raises(ValidationError):
        VapiWebhookRequest.model_validate({
            "message": {
                "type": "status-update",
            }
        })

def test_vapi_webhook_response_schema():
    from app.schemas.vapi import VapiWebhookResponse

    response = VapiWebhookResponse(
        status="ok",
        event_type="status-update",
        call_id="vapi-call-001",
    )

    assert response.status == "ok"
    assert response.event_type == "status-update"
    assert response.call_id == "vapi-call-001"
