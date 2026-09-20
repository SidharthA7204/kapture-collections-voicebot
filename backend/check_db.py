from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as connection:
    print("DATABASE:")
    print(
        connection.execute(
            text("""
                SELECT current_database(),
                       current_schema(),
                       current_user
            """)
        ).fetchone()
    )

    print("\nALEMBIC:")
    print(
        connection.execute(
            text("SELECT * FROM alembic_version")
        ).fetchall()
    )

    print("\nALL TABLES:")
    rows = connection.execute(
        text("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name
        """)
    ).fetchall()

    for row in rows:
        print(row)
