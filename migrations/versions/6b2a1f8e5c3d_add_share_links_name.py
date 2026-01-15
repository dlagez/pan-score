"""add share_links name

Revision ID: 6b2a1f8e5c3d
Revises: 4f9c1c7b8d2a
Create Date: 2026-01-14 19:18:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6b2a1f8e5c3d"
down_revision = "4f9c1c7b8d2a"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("share_links") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table("share_links") as batch_op:
        batch_op.drop_column("name")
