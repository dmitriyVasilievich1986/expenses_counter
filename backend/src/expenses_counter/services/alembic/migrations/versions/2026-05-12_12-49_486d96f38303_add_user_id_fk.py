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
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "486d96f38303"
down_revision = "c4e805302f9c"
branch_labels = None
depends_on = None


user = table("main_user", column("id"), column("username"), column("email"), column("password"))
transaction = table("main_transaction", column("id"), column("user_id"))


def upgrade():
    """Attach every transaction to a ``main_user`` row.

    Adds nullable ``user_id``, ensures at least one user exists for backfill,
    assigns the column from the lowest ``main_user.id``, then enforces
    ``NOT NULL`` and ``ON DELETE CASCADE`` on the foreign key.

    Returns:
        None

    """
    with op.batch_alter_table("main_transaction") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True))

    # Create a dummy user with a random password
    password = uuid4().hex

    connection = op.get_bind()
    user_id = connection.execute(
        user.insert().values(username="dummy", email="dummy@example.com", password=password).returning(user.c.id)
    ).fetchone()[0]
    connection.execute(transaction.update().values(user_id=user_id))

    with op.batch_alter_table("main_transaction") as batch_op:
        batch_op.alter_column("user_id", nullable=False)
        batch_op.create_foreign_key(
            "main_transaction_user_id_fkey", "main_user", ["user_id"], ["id"], ondelete="CASCADE"
        )


def downgrade():
    """Remove ``user_id`` from ``main_transaction`` and delete the placeholder user.

    Drops the foreign key and column, then removes the migration-only
    ``dummy`` user row if present.

    Returns:
        None

    """
    with op.batch_alter_table("main_transaction") as batch_op:
        batch_op.drop_constraint("main_transaction_user_id_fkey", type_="foreignkey")
        batch_op.drop_column("user_id")

    connection = op.get_bind()
    user_id = connection.execute(user.select().where(user.c.username == "dummy")).fetchone()[0]
    connection.execute(user.delete().where(user.c.id == user_id))
