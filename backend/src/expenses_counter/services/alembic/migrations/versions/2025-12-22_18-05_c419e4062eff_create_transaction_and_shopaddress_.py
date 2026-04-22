"""Create Transaction and ShopAddress tables migration.

Revision ID: c419e4062eff
Revises: d25b6ed05167
Create Date: 2025-12-22 18:05:24.742648

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c419e4062eff"
down_revision = "d25b6ed05167"
branch_labels = None
depends_on = None


def upgrade():
    """Refactor database schema to introduce Transaction and ShopAddress tables.

    This migration performs the following changes:
    1. Removes the 'date' field from main_price table
    2. Removes foreign key relationships from main_product (price_id, shop_id, sub_category_id)
    3. Removes the 'address' field from main_shop table
    4. Creates main_transaction table to track purchase transactions with date, price, product, shop, and subcategory
    5. Creates main_shopaddress table to store multiple addresses per shop

    This refactoring moves the transactional data from the product table to a dedicated
    transaction table, allowing products to exist independently of specific purchases.
    """
    # Remove field date from main_price
    with op.batch_alter_table("main_price") as batch_op:
        batch_op.drop_column("date")

    # Remove foreign key constraints and columns from main_product
    with op.batch_alter_table("main_product") as batch_op:
        batch_op.drop_constraint("main_product_price_id_fkey", type_="foreignkey")
        batch_op.drop_column("price_id")

        batch_op.drop_constraint("main_product_shop_id_fkey", type_="foreignkey")
        batch_op.drop_column("shop_id")

        batch_op.drop_constraint("main_product_sub_category_id_fkey", type_="foreignkey")
        batch_op.drop_column("sub_category_id")

    # Remove field address from main_shop
    with op.batch_alter_table("main_shop") as batch_op:
        batch_op.drop_column("address")

    # Create main_transaction table
    op.create_table(
        "main_transaction",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("date", sa.Date(), nullable=False, quote=True),
        sa.Column("price_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("shop_id", sa.BigInteger(), nullable=False),
        sa.Column("sub_category_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["price_id"], ["main_price.id"], ondelete="CASCADE", name="main_transaction_price_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["main_product.id"], ondelete="CASCADE", name="main_transaction_product_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["shop_id"], ["main_shop.id"], ondelete="CASCADE", name="main_transaction_shop_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["sub_category_id"],
            ["main_subcategory.id"],
            ondelete="CASCADE",
            name="main_transaction_sub_category_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="main_transaction_pkey"),
    )

    # Create main_shopaddress table
    op.create_table(
        "main_shopaddress",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("address", sa.String(length=150), nullable=False),
        sa.Column("shop_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["shop_id"], ["main_shop.id"], ondelete="CASCADE", name="main_shopaddress_shop_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="main_shopaddress_pkey"),
    )


def downgrade():
    """Revert the schema changes and restore the original structure.

    This downgrade performs the following:
    1. Drops the main_shopaddress and main_transaction tables
    2. Restores the 'address' column to main_shop table
    3. Restores foreign key columns to main_product (sub_category_id, shop_id, price_id)
    4. Restores the 'date' column to main_price table

    Note: This will result in data loss for any transactions and shop addresses
    that were created after this migration was applied.
    """
    # Drop the new tables
    op.drop_table("main_shopaddress")
    op.drop_table("main_transaction")

    # Re-add address column to main_shop
    with op.batch_alter_table("main_shop") as batch_op:
        batch_op.add_column(sa.Column("address", sa.String(length=150), nullable=True))

    # Re-add foreign key columns to main_product
    with op.batch_alter_table("main_product") as batch_op:
        batch_op.add_column(sa.Column("sub_category_id", sa.BigInteger(), nullable=False))
        batch_op.create_foreign_key(
            "main_product_sub_category_id_fkey", "main_subcategory", ["sub_category_id"], ["id"], ondelete="CASCADE"
        )

    with op.batch_alter_table("main_product") as batch_op:
        batch_op.add_column(sa.Column("shop_id", sa.BigInteger(), nullable=False))
        batch_op.create_foreign_key("main_product_shop_id_fkey", "main_shop", ["shop_id"], ["id"], ondelete="CASCADE")

    with op.batch_alter_table("main_product") as batch_op:
        batch_op.add_column(sa.Column("price_id", sa.BigInteger(), nullable=False))
        batch_op.create_foreign_key(
            "main_product_price_id_fkey", "main_price", ["price_id"], ["id"], ondelete="CASCADE"
        )

    # Re-add date column to main_price
    with op.batch_alter_table("main_price") as batch_op:
        batch_op.add_column(sa.Column("date", sa.Date(), nullable=False, quote=True))
