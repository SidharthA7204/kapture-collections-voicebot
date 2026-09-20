from datetime import date

from app.models.customer import Customer


class CustomerVerificationService:

    def verify(
        self,
        customer: Customer | None,
        phone: str,
        dob: date,
    ) -> bool:

        if customer is None:
            return False

        if customer.phone != phone:
            return False

        if customer.dob is None:
            return False

        return customer.dob.date() == dob