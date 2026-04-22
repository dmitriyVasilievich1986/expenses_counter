"""Add self to category table parent migration.

Revision ID: f68d0ab7444f
Revises: 7bc23a0f1288
Create Date: 2025-12-22 18:25:18.719461

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f68d0ab7444f"
down_revision = "7bc23a0f1288"
branch_labels = None
depends_on = None


def upgrade():
    """Add self-referential parent relationship to category table.

    Adds a nullable parent_id foreign key column to main_category table that
    references the same table. This creates a hierarchical tree structure for
    categories, allowing categories to have parent categories (e.g., "Electronics"
    as a parent of "Smartphones").

    The self-referential foreign key enables:
    - Multi-level category hierarchies
    - Parent-child category relationships
    - Category trees of arbitrary depth
    """
    with op.batch_alter_table("main_category") as batch_op:
        batch_op.add_column(sa.Column("parent_id", sa.BigInteger(), nullable=True))
        batch_op.create_foreign_key(
            "main_category_parent_id_fkey", "main_category", ["parent_id"], ["id"], ondelete="CASCADE"
        )


def downgrade():
    """Remove self-referential parent relationship from category table.

    Drops the foreign key constraint and removes the parent_id column from
    main_category table, eliminating the hierarchical structure and flattening
    all categories to a single level.
    """
    with op.batch_alter_table("main_category") as batch_op:
        batch_op.drop_constraint("main_category_parent_id_fkey", type_="foreignkey")
        batch_op.drop_column("parent_id")
