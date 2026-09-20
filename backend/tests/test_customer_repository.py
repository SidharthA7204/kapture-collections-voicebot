from app.db.repositories.customer_repository import CustomerRepository
from app.models.customer import Customer


def test_customer_repository_can_be_created(db_session):
    repository = CustomerRepository(db_session)

    assert repository is not None


def test_create_customer(db_session):
    repository = CustomerRepository(db_session)

    customer = Customer(
        name="Test Customer",
        phone="9876543210",
    )

    created_customer = repository.create(customer)

    assert created_customer.id is not None
    assert created_customer.name == "Test Customer"
    assert created_customer.phone == "9876543210"


def test_get_customer_by_id(db_session):
    repository = CustomerRepository(db_session)

    customer = Customer(
        name="Test Customer",
        phone="9876543211",
    )

    created_customer = repository.create(customer)

    result = repository.get_by_id(created_customer.id)

    assert result is not None
    assert result.id == created_customer.id
    assert result.name == "Test Customer"


def test_get_customer_by_phone(db_session):
    repository = CustomerRepository(db_session)

    customer = Customer(
        name="Phone Customer",
        phone="9876543212",
    )

    repository.create(customer)

    result = repository.get_by_phone("9876543212")

    assert result is not None
    assert result.name == "Phone Customer"
    assert result.phone == "9876543212"