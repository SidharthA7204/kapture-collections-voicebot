from enum import Enum


class IntentAction(str, Enum):
    PAYMENT = "PAYMENT"
    PROMISE_TO_PAY = "PROMISE_TO_PAY"
    DISPUTE = "DISPUTE"
    ASSISTANCE = "ASSISTANCE"
    CLARIFICATION = "CLARIFICATION"