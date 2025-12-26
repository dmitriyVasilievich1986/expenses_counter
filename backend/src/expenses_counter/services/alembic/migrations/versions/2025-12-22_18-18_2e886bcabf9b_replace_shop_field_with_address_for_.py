"""Replace shop field with address for transaction table migration.

Revision ID: 2e886bcabf9b
Revises: b49a0bf2e1e8
Create Date: 2025-12-22 18:18:36.870080

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2e886bcabf9b"
down_revision = "b49a0bf2e1e8"
branch_labels = None
depends_on = None


def upgrade():
    """Change transaction to reference shop address instead of shop.

    This migration refactors the main_transaction table to reference a specific
    shop address rather than the shop itself:
    1. Removes the shop_id foreign key and column
    2. Adds an address_id foreign key column referencing main_shopaddress

    This allows transactions to be associated with specific shop locations
    rather than just the shop brand/chain.
    """
    op.drop_constraint("main_transaction_shop_id_fkey", "main_transaction", type_="foreignkey")
    op.drop_column("main_transaction", "shop_id")
    op.add_column("main_transaction", sa.Column("address_id", sa.BigInteger(), nullable=False))
    op.create_foreign_key(
        "main_transaction_address_id_fkey",
        "main_transaction",
        "main_shopaddress",
        ["address_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    """Revert transaction to reference shop instead of shop address.

    This downgrade:
    1. Removes the address_id foreign key and column
    2. Restores the shop_id foreign key column referencing main_shop

    Note: This will result in data loss as address-specific information
    cannot be automatically converted back to shop references.
    """
    op.drop_constraint("main_transaction_address_id_fkey", "main_transaction", type_="foreignkey")
    op.drop_column("main_transaction", "address_id")
    op.add_column("main_transaction", sa.Column("shop_id", sa.BigInteger(), nullable=False))
    op.create_foreign_key(
        "main_transaction_shop_id_fkey", "main_transaction", "main_shop", ["shop_id"], ["id"], ondelete="CASCADE"
    )
