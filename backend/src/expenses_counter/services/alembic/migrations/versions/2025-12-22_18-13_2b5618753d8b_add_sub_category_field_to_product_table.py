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
    op.add_column("main_product", sa.Column("sub_category_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "main_product_sub_category_id_fkey",
        "main_product",
        "main_subcategory",
        ["sub_category_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    """Remove subcategory relationship from the product table.

    Drops the foreign key constraint and removes the sub_category_id column
    from the main_product table.
    """
    op.drop_constraint("main_product_sub_category_id_fkey", "main_product", type_="foreignkey")
    op.drop_column("main_product", "sub_category_id")
