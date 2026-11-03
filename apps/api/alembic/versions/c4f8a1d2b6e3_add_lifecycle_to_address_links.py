"""add lifecycle fields to address link tables

Revision ID: c4f8a1d2b6e3
Revises: e423c02db1c6
Create Date: 2026-11-02 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4f8a1d2b6e3"
down_revision: str | Sequence[str] | None = "e423c02db1c6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LINK_TABLES = ("customer_addresses", "supplier_addresses", "employee_addresses")


def upgrade() -> None:
    """Upgrade schema."""
    for table in LINK_TABLES:
        op.add_column(
            table,
            sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
        op.add_column(table, sa.Column("activated_at", sa.Date(), nullable=True))
        op.add_column(table, sa.Column("deactivated_at", sa.Date(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    for table in LINK_TABLES:
        op.drop_column(table, "deactivated_at")
        op.drop_column(table, "activated_at")
        op.drop_column(table, "active")
