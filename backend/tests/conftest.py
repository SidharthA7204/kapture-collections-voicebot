import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import Base


@pytest.fixture
def db_session():
    engine = create_engine(settings.DATABASE_URL)

    # Ensure the schema exists for tests that use the fixture.
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    # Clean test data without destroying the schema.
    with engine.begin() as connection:
        table_names = [
            table.name
            for table in reversed(Base.metadata.sorted_tables)
        ]

        for table_name in table_names:
            connection.execute(
                text(
                    f'TRUNCATE TABLE "{table_name}" '
                    "RESTART IDENTITY CASCADE"
                )
            )

    engine.dispose()