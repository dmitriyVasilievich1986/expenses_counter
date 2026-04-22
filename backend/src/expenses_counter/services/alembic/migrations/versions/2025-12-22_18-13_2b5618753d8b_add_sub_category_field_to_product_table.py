"""Add sub_category field to product table migration.

Revision ID: 2b5618753d8b
Revises: 3e0192741b18
Create Date: 2025-12-22 18:13:05.532140

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2b5618753d8b"
down_revision = "3e0192741b18"
branch_labels = None
depends_on = None


def upgrade():
    """Add subcategory relationship to the product table.

    Adds a nullable sub_category_id foreign key column to main_product table,
    allowing products to be associated with subcategories. The field is nullable
    to allow for products without assigned subcategories.
    """
    with op.batch_alter_table("main_product") as batch_op:
        batch_op.add_column(
            sa.Column("sub_category_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True)
        )
        batch_op.create_foreign_key(
            "main_product_sub_category_id_fkey", "main_subcategory", ["sub_category_id"], ["id"], ondelete="CASCADE"
        )


def downgrade():
    """Remove subcategory relationship from the product table.

    Drops the foreign key constraint and removes the sub_category_id column
    from the main_product table.
    """
    with op.batch_alter_table("main_product") as batch_op:
        batch_op.drop_constraint("main_product_sub_category_id_fkey", type_="foreignkey")
        batch_op.drop_column("sub_category_id")
