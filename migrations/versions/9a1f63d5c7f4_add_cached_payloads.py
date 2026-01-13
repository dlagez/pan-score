"""add cached payloads

Revision ID: 9a1f63d5c7f4
Revises: 6d504e687f8e
Create Date: 2026-01-13 20:05:24.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9a1f63d5c7f4"
down_revision = "6d504e687f8e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cached_payloads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cache_key", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cache_key", name="uq_cached_payloads_cache_key"),
    )


def downgrade():
    op.drop_table("cached_payloads")
