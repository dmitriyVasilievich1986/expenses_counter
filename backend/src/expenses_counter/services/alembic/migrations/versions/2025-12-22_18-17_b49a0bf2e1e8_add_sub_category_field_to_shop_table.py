"""Add sub_category field to shop table migration.

Revision ID: b49a0bf2e1e8
Revises: 017ee3dc6009
Create Date: 2025-12-22 18:17:42.700350

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b49a0bf2e1e8"
down_revision = "017ee3dc6009"
branch_labels = None
depends_on = None


def upgrade():
    """Add subcategory relationship to shop table.

    Adds a nullable sub_category_id foreign key column to main_shop table,
    allowing shops to be associated with subcategories. This enables
    categorization of shops (e.g., grocery store, electronics, etc.).
    """
    with op.batch_alter_table("main_shop") as batch_op:
        batch_op.add_column(
            sa.Column("sub_category_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True)
        )
        batch_op.create_foreign_key(
            "main_shop_sub_category_id_fkey", "main_subcategory", ["sub_category_id"], ["id"], ondelete="CASCADE"
        )


def downgrade():
    """Remove subcategory relationship from shop table.

    Drops the foreign key constraint and removes the sub_category_id column
    from the main_shop table.
    """
    with op.batch_alter_table("main_shop") as batch_op:
        batch_op.drop_constraint("main_shop_sub_category_id_fkey", type_="foreignkey")
        batch_op.drop_column("sub_category_id")
