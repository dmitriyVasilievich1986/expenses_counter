"""Create the ``main_user`` table for application accounts.

Linking ``main_transaction`` rows to users is introduced in a later revision.

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


def upgrade() -> None:
    """Create ``main_user`` with unique username and email constraints.

    Columns store login credentials; indexes support username lookups.

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


def downgrade() -> None:
    """Drop the ``main_user`` table.

    Returns:
        None

    """
    op.drop_table("main_user")
