from datetime import datetime

from ..extensions import db


class CachedPayload(db.Model):
    __tablename__ = "cached_payloads"

    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(255), unique=True, nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
