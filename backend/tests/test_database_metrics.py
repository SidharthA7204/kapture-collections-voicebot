from sqlalchemy import text

from app.core.db_metrics import (
    DB_CONNECTIONS_CHECKED_IN_TOTAL,
    DB_CONNECTIONS_CHECKED_OUT_TOTAL,
    DB_CONNECTIONS_IN_USE,
    DB_CONNECTION_POOL_SIZE,
)
from app.db.database import engine


def test_database_pool_size_metric():
    assert DB_CONNECTION_POOL_SIZE._value.get() > 0


def test_database_connection_metrics_record_usage():
    checked_out_before = (
        DB_CONNECTIONS_CHECKED_OUT_TOTAL._value.get()
    )
    checked_in_before = (
        DB_CONNECTIONS_CHECKED_IN_TOTAL._value.get()
    )

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    checked_out_after = (
        DB_CONNECTIONS_CHECKED_OUT_TOTAL._value.get()
    )
    checked_in_after = (
        DB_CONNECTIONS_CHECKED_IN_TOTAL._value.get()
    )

    assert checked_out_after > checked_out_before
    assert checked_in_after > checked_in_before


def test_database_connections_in_use_returns_to_zero():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

        assert DB_CONNECTIONS_IN_USE._value.get() >= 1

    assert DB_CONNECTIONS_IN_USE._value.get() == 0
