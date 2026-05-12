"""Add the user table and tie each transaction to a user.

Revision ID: c4e805302f9c
Revises: f68d0ab7444f
Create Date: 2026-05-12 09:28:31.103767

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c4e805302f9c"
down_revision = "f68d0ab7444f"
branch_labels = None
depends_on = None


def upgrade():
    """Create ``main_user`` and add ``user_id`` to ``main_transaction``.

    The new user row stores credentials and unique username and email keys.
    Each transaction references ``main_user`` with ``ON DELETE CASCADE``.

    Returns:
        None

    """
    op.create_table(
        "main_user",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("password", sa.String(length=150), nullable=False),
        sa.PrimaryKeyConstraint("id", name="main_user_pkey"),
        sa.UniqueConstraint("username", name="main_user_username_key"),
        sa.UniqueConstraint("email", name="main_user_email_key"),
        sa.Index("idx_main_user_username", "username"),
    )


def downgrade():
    """Drop the transaction ``user_id`` FK and remove ``main_user``.

    Returns:
        None

    """
    op.drop_table("main_user")
