from enum import Enum


class CustomerIntent(str, Enum):
    PAY_NOW = "PAY_NOW"
    PROMISE_TO_PAY = "PROMISE_TO_PAY"
    DISPUTE = "DISPUTE"
    UNABLE_TO_PAY = "UNABLE_TO_PAY"
    UNKNOWN = "UNKNOWN"