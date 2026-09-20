from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as connection:
    rows = connection.execute(
        text("""
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'call_logs'
            ORDER BY ordinal_position
        """)
    ).fetchall()

    print("CALL_LOGS:")
    for row in rows:
        print(row)
