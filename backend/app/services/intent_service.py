from app.schemas.intent import CustomerIntent
from app.schemas.intent_action import IntentAction


class IntentService:

    INTENT_ACTIONS = {
        CustomerIntent.PAY_NOW: IntentAction.PAYMENT,
        CustomerIntent.PROMISE_TO_PAY: IntentAction.PROMISE_TO_PAY,
        CustomerIntent.DISPUTE: IntentAction.DISPUTE,
        CustomerIntent.UNABLE_TO_PAY: IntentAction.ASSISTANCE,
        CustomerIntent.UNKNOWN: IntentAction.CLARIFICATION,
    }

    def determine_action(
        self,
        intent: CustomerIntent,
    ) -> IntentAction:
        return self.INTENT_ACTIONS[intent]