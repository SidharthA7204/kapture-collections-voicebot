from app.schemas.disposition import CallDisposition


def test_call_dispositions():
    assert (
        CallDisposition.PAYMENT_INITIATED.value
        == "PAYMENT_INITIATED"
    )

    assert (
        CallDisposition.PTP_COMMITTED.value
        == "PTP_COMMITTED"
    )

    assert (
        CallDisposition.DISPUTE_RAISED.value
        == "DISPUTE_RAISED"
    )

    assert (
        CallDisposition.NEGOTIATION_REQUIRED.value
        == "NEGOTIATION_REQUIRED"
    )

    assert (
        CallDisposition.HUMAN_ESCALATION.value
        == "HUMAN_ESCALATION"
    )

    assert (
        CallDisposition.CLARIFICATION_REQUIRED.value
        == "CLARIFICATION_REQUIRED"
    )