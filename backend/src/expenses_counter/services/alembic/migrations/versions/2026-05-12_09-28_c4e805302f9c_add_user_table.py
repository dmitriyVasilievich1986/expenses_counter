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

    with op.batch_alter_table("main_transaction") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False))
        batch_op.create_foreign_key(
            "main_transaction_user_id_fkey", "main_user", ["user_id"], ["id"], ondelete="CASCADE"
        )


def downgrade():
    """Drop the transaction ``user_id`` FK and remove ``main_user``.

    Returns:
        None

    """
    with op.batch_alter_table("main_transaction") as batch_op:
        batch_op.drop_constraint("main_transaction_user_id_fkey", type_="foreignkey")
        batch_op.drop_column("user_id")

    op.drop_table("main_user")
