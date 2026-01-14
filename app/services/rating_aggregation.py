from datetime import datetime
from sqlalchemy import func

from ..extensions import db
from ..models.link_rating import LinkRating
from ..models.share_link import ShareLink


def refresh_share_link_scores() -> int:
    """Recalculate avg_score/score_count from link_ratings."""
    aggregates = (
        db.session.query(
            LinkRating.share_link_id,
            func.avg(LinkRating.score).label("avg_score"),
            func.count(LinkRating.id).label("score_count"),
        )
        .group_by(LinkRating.share_link_id)
        .all()
    )

    aggregates_map = {row.share_link_id: row for row in aggregates}
    db.session.query(ShareLink).update(
        {
            ShareLink.avg_score: 0,
            ShareLink.score_count: 0,
            ShareLink.updated_at: datetime.utcnow(),
        }
    )

    for link_id, row in aggregates_map.items():
        db.session.query(ShareLink).filter_by(id=link_id).update(
            {
                ShareLink.avg_score: row.avg_score,
                ShareLink.score_count: row.score_count,
                ShareLink.updated_at: datetime.utcnow(),
            }
        )

    db.session.commit()
    return len(aggregates_map)
