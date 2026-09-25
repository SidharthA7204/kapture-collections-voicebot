from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings
from app.core.db_metrics import (
    DB_CONNECTIONS_CHECKED_IN_TOTAL,
    DB_CONNECTIONS_CHECKED_OUT_TOTAL,
    DB_CONNECTIONS_IN_USE,
    DB_CONNECTION_ERRORS_TOTAL,
    DB_CONNECTION_POOL_SIZE,
)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
)


DB_CONNECTION_POOL_SIZE.set(
    settings.DB_POOL_SIZE
)


@event.listens_for(engine, "checkout")
def database_connection_checked_out(
    dbapi_connection,
    connection_record,
    connection_proxy,
):
    DB_CONNECTIONS_CHECKED_OUT_TOTAL.inc()
    DB_CONNECTIONS_IN_USE.inc()


@event.listens_for(engine, "checkin")
def database_connection_checked_in(
    dbapi_connection,
    connection_record,
):
    DB_CONNECTIONS_CHECKED_IN_TOTAL.inc()
    DB_CONNECTIONS_IN_USE.dec()


@event.listens_for(engine, "invalidate")
def database_connection_invalidated(
    dbapi_connection,
    connection_record,
    exception,
):
    DB_CONNECTION_ERRORS_TOTAL.inc()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
