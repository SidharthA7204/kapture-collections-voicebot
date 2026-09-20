from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.dependencies import (
    get_call_event_service,
    get_call_flow_service,
)
from app.schemas.call import (
    StartCallRequest,
    StartCallResponse,
)
from app.schemas.call_action import (
    CallActionRequest,
    CallActionResponse,
)
from app.schemas.call_authentication import (
    AuthenticateCallResponse,
)
from app.schemas.call_event import (
    CallEventResponse,
    CallEventsResponse,
)
from app.schemas.call_termination import (
    CallTerminationResponse,
)
from app.schemas.call_transition import (
    TransitionCallRequest,
    TransitionCallResponse,
)
from app.schemas.customer_verification import (
    CustomerVerificationRequest,
    CustomerVerificationResponse,
)
from app.services.call_event_service import (
    CallEventService,
)
from app.services.call_flow_service import (
    CallFlowService,
)


router = APIRouter(
    prefix="/calls",
    tags=["calls"],
)


CallId = Annotated[
    str,
    Path(
        min_length=1,
        max_length=128,
    ),
]


@router.post(
    "/start",
    response_model=StartCallResponse,
)
def start_call(
    request: StartCallRequest,
    service: CallFlowService = Depends(
        get_call_flow_service
    ),
):
    machine, session, _ = service.start_call(
        call_id=request.call_id,
        customer_id=request.customer_id,
    )

    return StartCallResponse(
        call_id=session.call_id,
        customer_id=session.customer_id,
        current_state=machine.current_state.value,
        authenticated=session.authenticated,
    )


@router.post(
    "/{call_id}/transition",
    response_model=TransitionCallResponse,
)
def transition_call(
    call_id: CallId,
    request: TransitionCallRequest,
    service: CallFlowService = Depends(
        get_call_flow_service
    ),
):
    machine = service.restore_machine(
        call_id
    )

    result = service.transition(
        call_id=call_id,
        machine=machine,
        next_state=request.next_state,
    )

    return TransitionCallResponse(
        call_id=call_id,
        current_state=result.current_state,
    )


@router.post(
    "/{call_id}/authenticate",
    response_model=AuthenticateCallResponse,
)
def authenticate_call(
    call_id: CallId,
    service: CallFlowService = Depends(
        get_call_flow_service
    ),
):
    machine = service.restore_machine(
        call_id
    )

    session = service.authenticate(
        call_id=call_id,
        machine=machine,
    )

    return AuthenticateCallResponse(
        call_id=session.call_id,
        authenticated=session.authenticated,
        current_state=session.current_state,
    )


@router.post(
    "/{call_id}/verify-customer",
    response_model=CustomerVerificationResponse,
)
def verify_customer(
    call_id: CallId,
    request: CustomerVerificationRequest,
    service: CallFlowService = Depends(
        get_call_flow_service
    ),
):
    machine = service.restore_machine(
        call_id
    )

    result = service.verify_customer(
        call_id=call_id,
        machine=machine,
        phone=request.phone,
        dob=request.dob,
    )

    return CustomerVerificationResponse(
        call_id=call_id,
        authenticated=result["authenticated"],
        current_state=result["current_state"],
    )


@router.post(
    "/{call_id}/authentication-failed",
    response_model=CallTerminationResponse,
)
def authentication_failed(
    call_id: CallId,
    service: CallFlowService = Depends(
        get_call_flow_service
    ),
):
    machine = service.restore_machine(
        call_id
    )

    result = service.authentication_failed(
        call_id=call_id,
        machine=machine,
    )

    return CallTerminationResponse(
        call_id=call_id,
        current_state=result.current_state,
    )


@router.post(
    "/{call_id}/person-not-verified",
    response_model=CallTerminationResponse,
)
def person_not_verified(
    call_id: CallId,
    service: CallFlowService = Depends(
        get_call_flow_service
    ),
):
    machine = service.restore_machine(
        call_id
    )

    result = service.person_not_verified(
        call_id=call_id,
        machine=machine,
    )

    return CallTerminationResponse(
        call_id=call_id,
        current_state=result.current_state,
    )


@router.post(
    "/{call_id}/action",
    response_model=CallActionResponse,
)
def handle_call_action(
    call_id: CallId,
    request: CallActionRequest,
    service: CallFlowService = Depends(
        get_call_flow_service
    ),
):
    machine = service.restore_machine(
        call_id
    )

    disposition = service.handle_action(
        call_id=call_id,
        machine=machine,
        action=request.action,
        customer_id=request.customer_id,
        loan_id=request.loan_id,
        amount=request.amount,
        promise_date=request.promise_date,
    )

    return CallActionResponse(
        call_id=call_id,
        disposition=disposition.value,
    )


@router.post(
    "/{call_id}/end",
    response_model=CallTerminationResponse,
)
def end_call(
    call_id: CallId,
    service: CallFlowService = Depends(
        get_call_flow_service
    ),
):
    machine = service.restore_machine(
        call_id
    )

    result = service.end_call(
        call_id=call_id,
        machine=machine,
    )

    return CallTerminationResponse(
        call_id=call_id,
        current_state=machine.current_state.value,
    )


@router.get(
    "/{call_id}/events",
    response_model=CallEventsResponse,
)
def get_call_events(
    call_id: CallId,
    service: CallEventService = Depends(
        get_call_event_service
    ),
):
    events = service.get_call_events(
        call_id
    )

    return CallEventsResponse(
        call_id=call_id,
        events=[
            CallEventResponse(
                id=event.id,
                call_id=event.call_id,
                event_type=event.event_type,
                from_state=event.from_state,
                to_state=event.to_state,
                created_at=event.created_at,
            )
            for event in events
        ],
    )

