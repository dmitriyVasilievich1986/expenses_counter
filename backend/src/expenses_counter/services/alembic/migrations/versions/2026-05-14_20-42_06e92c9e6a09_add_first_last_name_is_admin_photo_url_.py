"""Extend ``main_user`` with profile fields and admin/active flags.

Adds optional first and last names, booleans ``is_admin`` and ``is_active``,
and an optional ``photo_url`` for account metadata.

Revision ID: 06e92c9e6a09
Revises: 486d96f38303
Create Date: 2026-05-14 20:42:57.180997

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "06e92c9e6a09"
down_revision = "486d96f38303"
branch_labels = None
depends_on = None


def upgrade():
    """Add profile and status columns to ``main_user``.

    Uses a batch alteration so SQLite and other backends apply the change
    consistently.

    Returns:
        None

    """
    with op.batch_alter_table("main_user") as batch_op:
        batch_op.add_column(sa.Column("first_name", sa.String(150), nullable=True))
        batch_op.add_column(sa.Column("last_name", sa.String(150), nullable=True))
        batch_op.add_column(sa.Column("is_admin", sa.Boolean, nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"))
        batch_op.add_column(sa.Column("photo_url", sa.String(255), nullable=True))


def downgrade():
    """Remove profile and status columns from ``main_user``.

    Returns:
        None

    """
    with op.batch_alter_table("main_user") as batch_op:
        batch_op.drop_column("first_name")
        batch_op.drop_column("last_name")
        batch_op.drop_column("is_admin")
        batch_op.drop_column("is_active")
        batch_op.drop_column("photo_url")
