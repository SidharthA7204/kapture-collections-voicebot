from app.schemas.payment import PaymentStatus


class PaymentService:

    def initiate_payment(
        self,
        customer_id: int,
        loan_id: int,
        amount,
    ) -> PaymentStatus:
        if amount <= 0:
            raise ValueError(
                "Payment amount must be greater than zero."
            )

        return PaymentStatus.INITIATED