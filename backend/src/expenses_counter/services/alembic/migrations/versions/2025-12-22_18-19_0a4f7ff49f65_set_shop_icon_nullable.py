"""Set shop icon nullable migration.

Revision ID: 0a4f7ff49f65
Revises: 2e886bcabf9b
Create Date: 2025-12-22 18:19:43.157053

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0a4f7ff49f65"
down_revision = "2e886bcabf9b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Make shop icon field nullable.

    Changes the icon column in main_shop table to allow NULL values.
    This provides flexibility for shops that don't have an icon/logo assigned.
    Note: The icon field was already nullable in a previous migration, so this
    may be ensuring the constraint is properly set.

    Returns:
        None

    """
    with op.batch_alter_table("main_shop") as batch_op:
        batch_op.alter_column("icon", nullable=True)


def downgrade() -> None:
    """Make shop icon field non-nullable.

    Changes the icon column in main_shop table to require a value (NOT NULL).
    Note: This downgrade may fail if there are existing shops with NULL icons.

    Returns:
        None

    """
    with op.batch_alter_table("main_shop") as batch_op:
        batch_op.alter_column("icon", nullable=False)
