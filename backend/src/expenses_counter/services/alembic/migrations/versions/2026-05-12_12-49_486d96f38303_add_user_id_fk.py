"""Add ``user_id`` to ``main_transaction`` with FK to ``main_user``.

Backfills existing rows with the lowest ``main_user.id``, then enforces
``NOT NULL`` and ``ON DELETE CASCADE`` on the foreign key.

Revision ID: 486d96f38303
Revises: c4e805302f9c
Create Date: 2026-05-12 12:49:27.940695

"""

from uuid import uuid4

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "486d96f38303"
down_revision = "c4e805302f9c"
branch_labels = None
depends_on = None


def upgrade():
    """Add nullable ``user_id``, backfill, require it, and add the FK.

    Returns:
        None

    """
    with op.batch_alter_table("main_transaction") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True))

    # Create a dummy user with a random password
    password = uuid4().hex
    op.execute(
        sa.text(
            """
            INSERT INTO main_user (username, email, password)
            VALUES ('dummy', 'dummy@example.com', :password)
        """,
            password=password,
        )
    )

    op.execute(
        sa.text("""
            UPDATE main_transaction
            SET user_id = (SELECT id FROM main_user ORDER BY id ASC LIMIT 1)
            WHERE user_id IS NULL
        """)
    )

    with op.batch_alter_table("main_transaction") as batch_op:
        batch_op.alter_column("user_id", nullable=False)
        batch_op.create_foreign_key(
            "main_transaction_user_id_fkey", "main_user", ["user_id"], ["id"], ondelete="CASCADE"
        )


def downgrade():
    """Remove the ``user_id`` foreign key and column from ``main_transaction``.

    Returns:
        None

    """
    with op.batch_alter_table("main_transaction") as batch_op:
        batch_op.drop_constraint("main_transaction_user_id_fkey", type_="foreignkey")
        batch_op.drop_column("user_id")

    op.execute(
        sa.text("""
            DELETE FROM main_user
            WHERE username = 'dummy'
        """)
    )
