from app.schemas.intent import CustomerIntent


def test_customer_intents():
    assert CustomerIntent.PAY_NOW.value == "PAY_NOW"
    assert CustomerIntent.PROMISE_TO_PAY.value == "PROMISE_TO_PAY"
    assert CustomerIntent.DISPUTE.value == "DISPUTE"
    assert CustomerIntent.UNABLE_TO_PAY.value == "UNABLE_TO_PAY"
    assert CustomerIntent.UNKNOWN.value == "UNKNOWN"