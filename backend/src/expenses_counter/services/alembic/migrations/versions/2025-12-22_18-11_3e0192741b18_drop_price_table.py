"""Drop Price table migration.

Revision ID: 3e0192741b18
Revises: 95009cbed51f
Create Date: 2025-12-22 18:11:48.137767

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3e0192741b18"
down_revision = "95009cbed51f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove the main_price table from the database.

    Since the previous migration changed transactions to store prices inline
    rather than as foreign key references, the main_price table is no longer
    needed and can be safely removed.

    Returns:
        None

    """
    op.drop_table("main_price")


def downgrade() -> None:
    """Recreate the main_price table.

    Restores the main_price table with its original structure:
    - id: BigInteger primary key
    - actual_price: Numeric(10, 2) for the actual paid price
    - full_price: Numeric(10, 2) for the original full price
    - date: Date field for when the price was recorded

    Note: This will create an empty table; historical price data cannot be restored.

    Returns:
        None

    """
    op.create_table(
        "main_price",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), autoincrement=True, nullable=False),
        sa.Column("actual_price", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("full_price", sa.Numeric(precision=10, scale=2), nullable=True, server_default="0"),
        sa.PrimaryKeyConstraint("id", name="main_price_pkey"),
    )
