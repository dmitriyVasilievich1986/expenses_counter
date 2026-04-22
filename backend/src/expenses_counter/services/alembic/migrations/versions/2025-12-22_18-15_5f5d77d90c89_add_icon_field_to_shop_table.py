"""Add icon field to shop table migration.

Revision ID: 5f5d77d90c89
Revises: 23f7346bac63
Create Date: 2025-12-22 18:15:59.879705

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5f5d77d90c89"
down_revision = "23f7346bac63"
branch_labels = None
depends_on = None


def upgrade():
    """Add icon field to shop table.

    Adds a nullable icon column (String, max 150 characters) to main_shop table.
    This field likely stores a file path or identifier for the shop's icon/logo.
    """
    with op.batch_alter_table("main_shop") as batch_op:
        batch_op.add_column(sa.Column("icon", sa.String(length=150), nullable=True))


def downgrade():
    """Remove icon field from shop table.

    Drops the icon column from main_shop table.
    """
    with op.batch_alter_table("main_shop") as batch_op:
        batch_op.drop_column("icon")
