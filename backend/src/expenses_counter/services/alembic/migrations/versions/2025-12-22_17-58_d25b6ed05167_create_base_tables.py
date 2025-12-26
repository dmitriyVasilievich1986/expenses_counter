"""Create base tables migration.

Revision ID: d25b6ed05167
Revises: 908132cc6ed4
Create Date: 2025-12-22 17:58:26.721576

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d25b6ed05167"
down_revision = "908132cc6ed4"
branch_labels = None
depends_on = None


def upgrade():
    """Create the base database tables for the expenses counter application.

    Creates the following tables:
    - main_category: Stores product categories with name and description
    - main_price: Stores price information with actual and full prices
    - main_shop: Stores shop information with address, name, and description
    - main_subcategory: Stores subcategories linked to main categories
    - main_product: Stores products with references to price, shop, and subcategory

    All tables use BigInteger for primary keys and include appropriate foreign key
    constraints with CASCADE delete behavior.
    """
    # Create main_category table
    op.create_table(
        "main_category",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create main_price table
    op.create_table(
        "main_price",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("actual_price", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("full_price", sa.Numeric(precision=10, scale=2), nullable=True, server_default="0"),
        sa.Column("date", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create main_shop table
    op.create_table(
        "main_shop",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("address", sa.String(length=150), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create main_subcategory table (depends on main_category)
    op.create_table(
        "main_subcategory",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["main_category.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create main_product table (depends on main_price, main_shop, main_subcategory)
    op.create_table(
        "main_product",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_id", sa.BigInteger(), nullable=False),
        sa.Column("shop_id", sa.BigInteger(), nullable=False),
        sa.Column("sub_category_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["price_id"], ["main_price.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["shop_id"], ["main_shop.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sub_category_id"], ["main_subcategory.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    """Drop all base tables created in the upgrade.

    Tables are dropped in reverse order to respect foreign key dependencies:
    1. main_product (has foreign keys to other tables)
    2. main_subcategory (has foreign key to main_category)
    3. main_shop
    4. main_price
    5. main_category
    """
    # Drop tables in reverse order (respecting foreign key dependencies)
    op.drop_table("main_product")
    op.drop_table("main_subcategory")
    op.drop_table("main_shop")
    op.drop_table("main_price")
    op.drop_table("main_category")
