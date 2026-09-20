from app.schemas.intent import CustomerIntent
from app.schemas.intent_action import IntentAction
from app.services.dispute_service import DisputeService
from app.services.intent_service import IntentService
from app.services.promise_to_pay_service import PromiseToPayService
from app.services.payment_service import PaymentService
from app.services.assistance_service import AssistanceService
from app.services.disposition_service import DispositionService
from app.services.call_log_service import CallLogService


class CollectionsIntentService:

    def __init__(
        self,
        intent_service: IntentService,
        dispute_service: DisputeService,
        promise_to_pay_service: PromiseToPayService,
        payment_service: PaymentService,
        assistance_service: AssistanceService,
        disposition_service: DispositionService,
        call_log_service: CallLogService,
    ):
        self.intent_service = intent_service
        self.dispute_service = dispute_service
        self.promise_to_pay_service = promise_to_pay_service
        self.payment_service = payment_service
        self.assistance_service = assistance_service
        self.disposition_service = disposition_service
        self.call_log_service = call_log_service

    def determine_action(
        self,
        intent: CustomerIntent,
    ) -> IntentAction:
        return self.intent_service.determine_action(intent)

    def create_dispute(
        self,
        customer_id: int,
        loan_id: int | None,
        reason: str,
        description: str | None = None,
    ):
        return self.dispute_service.create_dispute(
            customer_id=customer_id,
            loan_id=loan_id,
            reason=reason,
            description=description,
        )

    def create_promise(
        self,
        customer_id: int,
        loan_id: int,
        amount,
        promise_date,
        commit: bool = True,
    ):
        return self.promise_to_pay_service.create_promise(
            customer_id=customer_id,
            loan_id=loan_id,
            amount=amount,
            promise_date=promise_date,
            commit=commit,
        )

    def initiate_payment(
        self,
        customer_id: int,
        loan_id: int,
        amount,
    ):
        return self.payment_service.initiate_payment(
            customer_id=customer_id,
            loan_id=loan_id,
            amount=amount,
        )

    def handle_unable_to_pay(
        self,
        customer_id: int,
        loan_id: int,
    ):
        return self.assistance_service.handle_unable_to_pay(
            customer_id=customer_id,
            loan_id=loan_id,
        )

    def determine_disposition(
        self,
        action: IntentAction,
    ):
        return self.disposition_service.determine_disposition(
            action
        )

    def record_call_disposition(
        self,
        call_id: str,
        action: IntentAction,
        commit: bool = True,
    ):
        disposition = self.determine_disposition(action)

        return self.call_log_service.record_disposition(
            call_id=call_id,
            disposition=disposition.value,
            commit=commit,
        )
