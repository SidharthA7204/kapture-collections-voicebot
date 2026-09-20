from app.db.repositories.customer_repository import CustomerRepository
from app.models.customer import Customer


class CustomerService:

    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    def get_customer_by_id(
        self,
        customer_id: int,
    ) -> Customer | None:
        return self.repository.get_by_id(customer_id)

    def get_customer_by_phone(
        self,
        phone: str,
    ) -> Customer | None:
        return self.repository.get_by_phone(phone)

    def create_customer(
        self,
        customer: Customer,
    ) -> Customer:
        return self.repository.create(customer)