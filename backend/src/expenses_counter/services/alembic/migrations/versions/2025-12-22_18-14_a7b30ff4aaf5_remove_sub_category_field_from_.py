"""Remove sub_category field from transaction table migration.

Revision ID: a7b30ff4aaf5
Revises: 2b5618753d8b
Create Date: 2025-12-22 18:14:08.740193

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a7b30ff4aaf5"
down_revision = "2b5618753d8b"
branch_labels = None
depends_on = None


def upgrade():
    """Remove subcategory reference from transaction table.

    Removes the sub_category_id column from main_transaction table.
    This is likely because subcategory information can be derived from
    the product relationship instead of being stored redundantly.
    """
    op.drop_column("main_transaction", "sub_category_id")


def downgrade():
    """Restore subcategory reference to transaction table.

    Re-adds the nullable sub_category_id foreign key column to main_transaction
    and recreates the foreign key constraint to main_subcategory table.
    """
    op.add_column("main_transaction", sa.Column("sub_category_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "main_transaction_sub_category_id_fkey",
        "main_transaction",
        "main_subcategory",
        ["sub_category_id"],
        ["id"],
        ondelete="CASCADE",
    )
