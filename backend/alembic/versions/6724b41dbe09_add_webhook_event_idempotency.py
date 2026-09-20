"""add webhook event idempotency

Revision ID: 6724b41dbe09
Revises: 4cf8b97a29fe
Create Date: 2026-09-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6724b41dbe09"
down_revision: Union[str, Sequence[str], None] = "4cf8b97a29fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "webhook_events",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "provider",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "event_id",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "event_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "call_id",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "processed_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider",
            "event_id",
            name="uq_webhook_events_provider_event_id",
        ),
    )

    op.create_index(
        "ix_webhook_events_provider",
        "webhook_events",
        ["provider"],
        unique=False,
    )

    op.create_index(
        "ix_webhook_events_call_id",
        "webhook_events",
        ["call_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_webhook_events_call_id",
        table_name="webhook_events",
    )

    op.drop_index(
        "ix_webhook_events_provider",
        table_name="webhook_events",
    )

    op.drop_table("webhook_events")
