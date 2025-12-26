"""Switch sub_category field with category migration.

Revision ID: 7bc23a0f1288
Revises: 0a4f7ff49f65
Create Date: 2025-12-22 18:21:16.521561

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7bc23a0f1288"
down_revision = "0a4f7ff49f65"
branch_labels = None
depends_on = None


def upgrade():
    """Replace subcategory references with category references.

    This migration refactors both main_shop and main_product tables to reference
    main_category instead of main_subcategory:

    For main_shop:
    1. Drops sub_category_id foreign key and column
    2. Adds category_id foreign key column referencing main_category

    For main_product:
    1. Drops sub_category_id foreign key and column
    2. Adds category_id foreign key column referencing main_category

    This simplifies the data model by using categories directly instead of
    requiring subcategories.
    """
    op.drop_constraint("main_shop_sub_category_id_fkey", "main_shop", type_="foreignkey")
    op.drop_column("main_shop", "sub_category_id")
    op.add_column("main_shop", sa.Column("category_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "main_shop_category_id_fkey", "main_shop", "main_category", ["category_id"], ["id"], ondelete="CASCADE"
    )

    op.drop_constraint("main_product_sub_category_id_fkey", "main_product", type_="foreignkey")
    op.drop_column("main_product", "sub_category_id")
    op.add_column("main_product", sa.Column("category_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "main_product_category_id_fkey", "main_product", "main_category", ["category_id"], ["id"], ondelete="CASCADE"
    )


def downgrade():
    """Revert category references back to subcategory references.

    This downgrade restores the original structure:

    For main_shop:
    1. Drops category_id foreign key and column
    2. Restores sub_category_id foreign key column

    For main_product:
    1. Drops category_id foreign key and column
    2. Restores sub_category_id foreign key column

    Note: This will result in data loss as category references cannot be
    automatically converted back to subcategory references.
    """
    op.drop_constraint("main_shop_sub_category_id_fkey", "main_shop", type_="foreignkey")
    op.drop_column("main_shop", "sub_category_id")
    op.add_column("main_shop", sa.Column("category_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "main_shop_category_id_fkey", "main_shop", "main_category", ["category_id"], ["id"], ondelete="CASCADE"
    )

    op.drop_constraint("main_product_category_id_fkey", "main_product", type_="foreignkey")
    op.drop_column("main_product", "category_id")
    op.add_column("main_product", sa.Column("sub_category_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "main_product_sub_category_id_fkey",
        "main_product",
        "main_subcategory",
        ["sub_category_id"],
        ["id"],
        ondelete="CASCADE",
    )
