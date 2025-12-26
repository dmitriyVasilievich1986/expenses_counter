"""Add count field to transaction table migration.

Revision ID: 017ee3dc6009
Revises: 5f5d77d90c89
Create Date: 2025-12-22 18:17:07.839835

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "017ee3dc6009"
down_revision = "5f5d77d90c89"
branch_labels = None
depends_on = None


def upgrade():
    """Add quantity/count field to transaction table.

    Adds a non-nullable count column (Numeric with precision 10 and scale 3)
    to main_transaction table with a default value of 0. This field tracks
    the quantity of items purchased in each transaction, supporting decimal
    quantities (e.g., 1.5 kg of produce).
    """
    op.add_column(
        "main_transaction", sa.Column("count", sa.Numeric(precision=10, scale=3), nullable=False, server_default="0")
    )


def downgrade():
    """Remove quantity/count field from transaction table.

    Drops the count column from main_transaction table.
    """
    op.drop_column("main_transaction", "count")
