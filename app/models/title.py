from datetime import datetime
from sqlalchemy import UniqueConstraint
from ..extensions import db


class Title(db.Model):
    __tablename__ = "titles"
    __table_args__ = (
        UniqueConstraint("tmdb_id", "media_type", name="uq_titles_tmdb_media"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, nullable=False)
    media_type = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255))
    release_date = db.Column(db.Date)
    first_air_date = db.Column(db.Date)
    poster_path = db.Column(db.String(255))
    status = db.Column(db.String(80))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    share_links = db.relationship("ShareLink", back_populates="title", cascade="all, delete-orphan")
