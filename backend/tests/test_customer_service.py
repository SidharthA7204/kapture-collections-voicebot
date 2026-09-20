from app.db.repositories.customer_repository import CustomerRepository
from app.models.customer import Customer
from app.services.customer_service import CustomerService


def test_customer_service_can_be_created(db_session):
    repository = CustomerRepository(db_session)
    service = CustomerService(repository)

    assert service is not None


def test_get_customer_by_id(db_session):
    repository = CustomerRepository(db_session)
    service = CustomerService(repository)

    customer = Customer(
        name="Service Customer",
        phone="9876543220",
    )

    created_customer = repository.create(customer)

    result = service.get_customer_by_id(created_customer.id)

    assert result is not None
    assert result.id == created_customer.id
    assert result.name == "Service Customer"


def test_get_customer_by_phone(db_session):
    repository = CustomerRepository(db_session)
    service = CustomerService(repository)

    customer = Customer(
        name="Phone Service Customer",
        phone="9876543221",
    )

    repository.create(customer)

    result = service.get_customer_by_phone("9876543221")

    assert result is not None
    assert result.phone == "9876543221"


def test_create_customer(db_session):
    repository = CustomerRepository(db_session)
    service = CustomerService(repository)

    customer = Customer(
        name="New Customer",
        phone="9876543222",
    )

    result = service.create_customer(customer)

    assert result.id is not None
    assert result.name == "New Customer"
    assert result.phone == "9876543222"