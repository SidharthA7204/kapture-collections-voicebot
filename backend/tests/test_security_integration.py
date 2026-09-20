from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_call_flow_service
from app.middleware.request_context import (
    RequestContextMiddleware,
)
from app.routes.calls import router


def test_verification_security_integration(
    db_session,
):
    from tests.test_call_termination_consistency import (
        create_customer,
        create_service,
        move_to_authentication,
    )

    customer = create_customer(db_session)
    service = create_service(db_session)

    call_id = "security_integration_001"

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=customer.id,
    )

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    app = FastAPI()

    app.add_middleware(
        RequestContextMiddleware
    )

    app.include_router(router)

    app.dependency_overrides[
        get_call_flow_service
    ] = lambda: service

    try:
        client = TestClient(app)

        request_id = "security-integration-001"

        for attempt in range(3):
            response = client.post(
                f"/calls/{call_id}/verify-customer",
                headers={
                    "X-Request-ID": request_id,
                },
                json={
                    "phone": "9999999999",
                    "dob": "1995-05-15",
                },
            )

            assert response.status_code == 200

            assert (
                response.headers["X-Request-ID"]
                == request_id
            )

            data = response.json()

            assert "phone" not in data
            assert "dob" not in data

            if attempt < 2:
                assert data["authenticated"] is False
                assert data["current_state"] == (
                    "AUTHENTICATION"
                )

        assert data["authenticated"] is False
        assert data["current_state"] == "END"

    finally:
        app.dependency_overrides.clear()
