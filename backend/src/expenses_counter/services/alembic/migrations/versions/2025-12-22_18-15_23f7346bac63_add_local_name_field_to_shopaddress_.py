"""Add local_name field to shopaddress table migration.

Revision ID: 23f7346bac63
Revises: a7b30ff4aaf5
Create Date: 2025-12-22 18:15:02.400478

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "23f7346bac63"
down_revision = "a7b30ff4aaf5"
branch_labels = None
depends_on = None


def upgrade():
    """Add local_name field to shop address table.

    Adds a non-nullable local_name column (String, max 150 characters) to
    main_shopaddress table. This field likely stores a localized or custom
    name for the specific shop location/address.
    """
    with op.batch_alter_table("main_shopaddress") as batch_op:
        batch_op.add_column(sa.Column("local_name", sa.String(length=150), nullable=False))


def downgrade():
    """Remove local_name field from shop address table.

    Drops the local_name column from main_shopaddress table.
    """
    with op.batch_alter_table("main_shopaddress") as batch_op:
        batch_op.drop_column("local_name")
