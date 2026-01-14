from datetime import datetime
from sqlalchemy import UniqueConstraint
from ..extensions import db


class ShareLink(db.Model):
    __tablename__ = "share_links"
    __table_args__ = (
        UniqueConstraint("url", name="uq_share_links_url"),
    )

    id = db.Column(db.Integer, primary_key=True)
    title_id = db.Column(db.Integer, db.ForeignKey("titles.id"), nullable=False, index=True)
    provider = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(1024), nullable=False)
    access_code = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    avg_score = db.Column(db.Numeric(3, 2), default=0, nullable=False)
    score_count = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    title = db.relationship("Title", back_populates="share_links")
    ratings = db.relationship("LinkRating", back_populates="share_link", cascade="all, delete-orphan")
