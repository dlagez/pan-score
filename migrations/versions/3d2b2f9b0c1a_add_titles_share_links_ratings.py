"""add titles share links ratings

Revision ID: 3d2b2f9b0c1a
Revises: 9a1f63d5c7f4
Create Date: 2026-01-14 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3d2b2f9b0c1a"
down_revision = "9a1f63d5c7f4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "titles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tmdb_id", sa.Integer(), nullable=False),
        sa.Column("media_type", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=True),
        sa.Column("release_date", sa.Date(), nullable=True),
        sa.Column("first_air_date", sa.Date(), nullable=True),
        sa.Column("poster_path", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tmdb_id", "media_type", name="uq_titles_tmdb_media"),
    )

    op.create_table(
        "share_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("access_code", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("avg_score", sa.Numeric(3, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("score_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["title_id"], ["titles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url", name="uq_share_links_url"),
    )
    op.create_index("ix_share_links_title_id", "share_links", ["title_id"])

    op.create_table(
        "link_ratings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("share_link_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Numeric(2, 1), nullable=False),
        sa.Column("comment", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("score >= 1 AND score <= 5", name="ck_link_ratings_score"),
        sa.ForeignKeyConstraint(["share_link_id"], ["share_links.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "share_link_id", name="uq_link_ratings_user_link"),
    )
    op.create_index("ix_link_ratings_share_link_id", "link_ratings", ["share_link_id"])
    op.create_index("ix_link_ratings_user_id", "link_ratings", ["user_id"])


def downgrade():
    op.drop_index("ix_link_ratings_user_id", table_name="link_ratings")
    op.drop_index("ix_link_ratings_share_link_id", table_name="link_ratings")
    op.drop_table("link_ratings")
    op.drop_index("ix_share_links_title_id", table_name="share_links")
    op.drop_table("share_links")
    op.drop_table("titles")
