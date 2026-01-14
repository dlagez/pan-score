from datetime import datetime
from sqlalchemy import CheckConstraint, UniqueConstraint
from ..extensions import db


class LinkRating(db.Model):
    __tablename__ = "link_ratings"
    __table_args__ = (
        UniqueConstraint("user_id", "share_link_id", name="uq_link_ratings_user_link"),
        CheckConstraint("score >= 1 AND score <= 5", name="ck_link_ratings_score"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    share_link_id = db.Column(db.Integer, db.ForeignKey("share_links.id"), nullable=False, index=True)
    score = db.Column(db.Numeric(2, 1), nullable=False)
    comment = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    share_link = db.relationship("ShareLink", back_populates="ratings")
    user = db.relationship("User")
