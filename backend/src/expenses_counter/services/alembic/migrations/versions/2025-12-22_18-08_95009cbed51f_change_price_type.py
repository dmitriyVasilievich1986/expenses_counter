"""Change price type migration.

Revision ID: 95009cbed51f
Revises: c419e4062eff
Create Date: 2025-12-22 18:08:03.214226

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "95009cbed51f"
down_revision = "c419e4062eff"
branch_labels = None
depends_on = None


def upgrade():
    """Change price storage from foreign key reference to inline decimal field.

    This migration refactors the main_transaction table to store price directly
    as a decimal field instead of referencing the main_price table:
    1. Drops the foreign key constraint to main_price
    2. Removes the price_id column
    3. Adds a new 'price' column as Numeric(10, 2) with default value 0

    This simplifies the data model by eliminating the need for a separate price table
    for transaction records.
    """
    # Drop the foreign key constraint first
    op.drop_constraint("main_transaction_price_id_fkey", "main_transaction", type_="foreignkey")

    # Drop the old price_id column
    op.drop_column("main_transaction", "price_id")

    # Add the new price column as a decimal field
    op.add_column(
        "main_transaction", sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0")
    )


def downgrade():
    """Revert price storage back to foreign key reference.

    This downgrade:
    1. Removes the inline 'price' decimal column
    2. Restores the price_id foreign key column
    3. Re-creates the foreign key constraint to main_price table

    Note: This will result in data loss as existing price values cannot be
    automatically converted back to price_id references.
    """
    # Drop the decimal price column
    op.drop_column("main_transaction", "price")

    # Re-add the price_id foreign key column
    op.add_column("main_transaction", sa.Column("price_id", sa.BigInteger(), nullable=False))

    # Re-create the foreign key constraint
    op.create_foreign_key(
        "main_transaction_price_id_fkey", "main_transaction", "main_price", ["price_id"], ["id"], ondelete="CASCADE"
    )
