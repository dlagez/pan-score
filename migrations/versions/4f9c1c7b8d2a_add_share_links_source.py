"""add share_links source

Revision ID: 4f9c1c7b8d2a
Revises: 3d2b2f9b0c1a
Create Date: 2026-01-14 19:02:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4f9c1c7b8d2a"
down_revision = "3d2b2f9b0c1a"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("share_links") as batch_op:
        batch_op.add_column(
            sa.Column("source", sa.String(length=32), nullable=False, server_default="manual")
        )


def downgrade():
    with op.batch_alter_table("share_links") as batch_op:
        batch_op.drop_column("source")
