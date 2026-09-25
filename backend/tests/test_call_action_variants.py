import pytest
from decimal import Decimal
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.db.database import get_db
from app.main import app
from app.models.customer import Customer
from app.models.loan import Loan


@pytest.mark.parametrize(
    "action,expected_disposition",
    [
        ("PROMISE_TO_PAY", "PTP_COMMITTED"),
        ("DISPUTE", "DISPUTE_RAISED"),
        ("ASSISTANCE", "NEGOTIATION_REQUIRED"),
        ("CLARIFICATION", "CLARIFICATION_REQUIRED"),
    ],
)
def test_action_variants(
    db_session,
    action,
    expected_disposition,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        call_id = f"action_variant_{action.lower()}"

        customer_id = None
        loan_id = None

        if action in ("PROMISE_TO_PAY", "DISPUTE"):
            customer = Customer(
                name=f"{action} Test Customer",
                phone=f"94000000{10 if action == 'PROMISE_TO_PAY' else '11'}",
            )

            db_session.add(customer)
            db_session.commit()
            db_session.refresh(customer)

            loan = Loan(
                customer_id=customer.id,
                loan_type="PERSONAL",
                overdue_amount=Decimal("15000.00"),
                days_past_due=30,
            )

            db_session.add(loan)
            db_session.commit()
            db_session.refresh(loan)

            customer_id = customer.id
            loan_id = loan.id

        response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": customer_id,
            },
        )

        assert response.status_code == 200

        for state in (
            "INTRODUCTION",
            "CHECK_PERSON",
            "AUTHENTICATION",
            "DISCLOSE_OVERDUE",
            "INTENT_HANDLING",
        ):
            response = client.post(
                f"/calls/{call_id}/transition",
                json={
                    "next_state": state,
                },
            )

            assert response.status_code == 200

        action_body = {
            "action": action,
        }

        if action in ("PROMISE_TO_PAY", "DISPUTE"):
            action_body.update(
                {
                    "customer_id": customer_id,
                    "loan_id": loan_id,
                }
            )

        if action == "PROMISE_TO_PAY":
            action_body.update(
                {
                    "amount": "5000.00",
                    "promise_date": (
                        date.today()
                        + timedelta(days=7)
                    ).isoformat(),
                }
            )

        response = client.post(
            f"/calls/{call_id}/action",
            json=action_body,
        )

        if response.status_code != 200:
            print("ACTION API ERROR:", response.status_code)
            print("ACTION API BODY:", response.text)

        assert response.status_code == 200

        data = response.json()

        assert data["call_id"] == call_id
        assert data["disposition"] == expected_disposition

    finally:
        app.dependency_overrides.clear()
