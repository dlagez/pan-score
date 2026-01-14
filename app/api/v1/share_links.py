from datetime import datetime
from decimal import Decimal
from urllib import parse as urlparse

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from ...extensions import db
from ...models.link_rating import LinkRating
from ...models.share_link import ShareLink
from ...models.title import Title
from ...services.rating_aggregation import refresh_share_link_scores
from . import v1_bp


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def _resolve_provider(url: str) -> str:
    host = urlparse.urlparse(url).netloc.lower()
    if not host:
        return "unknown"
    if "pan.baidu.com" in host:
        return "baidu"
    if "pan.quark.cn" in host:
        return "quark"
    if "aliyundrive.com" in host or "alipan.com" in host:
        return "aliyun"
    if "onedrive" in host:
        return "onedrive"
    return host


def _link_payload(link: ShareLink) -> dict:
    return {
        "id": link.id,
        "title_id": link.title_id,
        "provider": link.provider,
        "url": link.url,
        "access_code": link.access_code,
        "avg_score": float(link.avg_score or 0),
        "score_count": link.score_count or 0,
    }


@v1_bp.get("/share-links")
def share_links_list():
    tmdb_id = request.args.get("tmdb_id", type=int)
    media_type = request.args.get("media_type", type=str)
    if not tmdb_id or not media_type:
        return {"error": "MISSING_PARAMS"}, 400

    title = Title.query.filter_by(tmdb_id=tmdb_id, media_type=media_type).first()
    if not title:
        return {"results": []}, 200

    links = (
        ShareLink.query.filter_by(title_id=title.id, is_active=True)
        .order_by(ShareLink.avg_score.desc(), ShareLink.score_count.desc(), ShareLink.id.desc())
        .all()
    )
    return {"results": [_link_payload(link) for link in links]}, 200


@v1_bp.get("/share-links/ratings")
@jwt_required()
def share_links_user_ratings():
    tmdb_id = request.args.get("tmdb_id", type=int)
    media_type = request.args.get("media_type", type=str)
    if not tmdb_id or not media_type:
        return {"error": "MISSING_PARAMS"}, 400

    user_id = int(get_jwt_identity())
    title = Title.query.filter_by(tmdb_id=tmdb_id, media_type=media_type).first()
    if not title:
        return {"ratings": []}, 200

    ratings = (
        db.session.query(LinkRating.share_link_id, LinkRating.score)
        .join(ShareLink, ShareLink.id == LinkRating.share_link_id)
        .filter(ShareLink.title_id == title.id, LinkRating.user_id == user_id)
        .all()
    )

    return {
        "ratings": [
            {"link_id": link_id, "score": float(score)} for link_id, score in ratings
        ]
    }, 200


@v1_bp.post("/share-links")
def share_links_create():
    data = request.get_json(silent=True) or {}
    tmdb_id = data.get("tmdb_id")
    media_type = data.get("media_type")
    url = (data.get("url") or "").strip()
    if not tmdb_id or not media_type or not url:
        return {"error": "MISSING_PARAMS"}, 400

    try:
        tmdb_id = int(tmdb_id)
    except (TypeError, ValueError):
        return {"error": "INVALID_TMDB_ID"}, 400

    media_type = media_type.strip()
    if media_type not in {"movie", "tv"}:
        return {"error": "INVALID_MEDIA_TYPE"}, 400

    title = Title.query.filter_by(tmdb_id=tmdb_id, media_type=media_type).first()
    if not title:
        title = Title(
            tmdb_id=tmdb_id,
            media_type=media_type,
            name=data.get("name") or data.get("title") or "未命名",
            original_name=data.get("original_name") or data.get("original_title"),
            release_date=_parse_date(data.get("release_date")),
            first_air_date=_parse_date(data.get("first_air_date")),
            poster_path=data.get("poster_path"),
            status=data.get("status"),
        )
        db.session.add(title)
    else:
        if not title.name and (data.get("name") or data.get("title")):
            title.name = data.get("name") or data.get("title")
        if not title.original_name and (data.get("original_name") or data.get("original_title")):
            title.original_name = data.get("original_name") or data.get("original_title")
        if not title.release_date and data.get("release_date"):
            title.release_date = _parse_date(data.get("release_date"))
        if not title.first_air_date and data.get("first_air_date"):
            title.first_air_date = _parse_date(data.get("first_air_date"))
        if not title.poster_path and data.get("poster_path"):
            title.poster_path = data.get("poster_path")
        if not title.status and data.get("status"):
            title.status = data.get("status")

    if title.id is None:
        db.session.flush()

    provider = (data.get("provider") or "").strip() or _resolve_provider(url)
    access_code = (data.get("access_code") or "").strip() or None

    link = ShareLink(
        title=title,
        provider=provider,
        url=url,
        access_code=access_code,
    )
    db.session.add(link)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "LINK_EXISTS"}, 409

    return {"link": _link_payload(link)}, 201


@v1_bp.post("/share-links/<int:link_id>/rating")
@jwt_required()
def share_links_rate(link_id: int):
    data = request.get_json(silent=True) or {}
    score_value = data.get("score")
    if score_value is None:
        return {"error": "MISSING_SCORE"}, 400

    try:
        score = Decimal(str(score_value))
    except Exception:
        return {"error": "INVALID_SCORE"}, 400

    if score < 1 or score > 5:
        return {"error": "INVALID_SCORE"}, 400

    if (score * 2) % 1 != 0:
        return {"error": "INVALID_SCORE_STEP"}, 400

    user_id = int(get_jwt_identity())
    link = ShareLink.query.get(link_id)
    if not link:
        return {"error": "NOT_FOUND"}, 404

    existing = LinkRating.query.filter_by(user_id=user_id, share_link_id=link_id).first()

    if existing:
        existing.score = score
        existing.updated_at = datetime.utcnow()
        db.session.commit()
        return {"link": _link_payload(link), "user_score": float(score)}, 200

    new_rating = LinkRating(user_id=user_id, share_link_id=link_id, score=score)
    db.session.add(new_rating)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        existing = LinkRating.query.filter_by(user_id=user_id, share_link_id=link_id).first()
        if not existing:
            return {"error": "RATE_FAILED"}, 500
        existing.score = score
        existing.updated_at = datetime.utcnow()
        db.session.commit()

    return {"link": _link_payload(link), "user_score": float(score)}, 200


@v1_bp.post("/share-links/refresh-scores")
def share_links_refresh_scores():
    updated = refresh_share_link_scores()
    return {"updated": updated}, 200
