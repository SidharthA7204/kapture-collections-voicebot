from app.schemas.disposition import CallDisposition
from app.schemas.intent_action import IntentAction


class DispositionService:

    ACTION_TO_DISPOSITION = {
        IntentAction.PAYMENT: CallDisposition.PAYMENT_INITIATED,
        IntentAction.PROMISE_TO_PAY: CallDisposition.PTP_COMMITTED,
        IntentAction.DISPUTE: CallDisposition.DISPUTE_RAISED,
        IntentAction.ASSISTANCE: CallDisposition.NEGOTIATION_REQUIRED,
        IntentAction.CLARIFICATION: CallDisposition.CLARIFICATION_REQUIRED,
    }

    def determine_disposition(
        self,
        action: IntentAction,
    ) -> CallDisposition:
        try:
            return self.ACTION_TO_DISPOSITION[action]
        except KeyError:
            raise ValueError(
                f"Unsupported intent action: {action}"
            )