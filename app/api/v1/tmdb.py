import json
from datetime import datetime, timedelta
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest

from flask import current_app, request

from ...extensions import db
from ...models.cache import CachedPayload
from . import v1_bp

CACHE_TTL = timedelta(hours=24)


def _normalize_params(params: dict) -> dict:
    normalized = dict(params)
    language = current_app.config.get("TMDB_LANGUAGE")
    if language and "language" not in normalized:
        normalized["language"] = language
    return normalized


def _language_param() -> dict:
    language = request.args.get("language")
    return {"language": language} if language else {}


def _build_cache_key(path: str, params: dict) -> str:
    query = urlparse.urlencode(sorted(params.items()))
    return f"{path}?{query}"


def _is_expired(updated_at: datetime) -> bool:
    return datetime.utcnow() - updated_at > CACHE_TTL


def _tmdb_fetch(path: str, params: dict) -> tuple[dict, int]:
    base_url = current_app.config.get("TMDB_BASE_URL")
    access_token = current_app.config.get("TMDB_ACCESS_TOKEN")
    api_key = current_app.config.get("TMDB_API_KEY")

    if not access_token and not api_key:
        return {"error": "TMDB_KEY_MISSING"}, 500

    headers = {"Accept": "application/json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    else:
        params["api_key"] = api_key

    query = urlparse.urlencode(params)
    url = f"{base_url}{path}?{query}"
    req = urlrequest.Request(url, headers=headers)

    try:
        with urlrequest.urlopen(req, timeout=10) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload), resp.status
    except urlerror.HTTPError as exc:
        payload = exc.read().decode("utf-8")
        try:
            return json.loads(payload), exc.code
        except json.JSONDecodeError:
            return {"error": "TMDB_BAD_RESPONSE"}, exc.code
    except urlerror.URLError:
        return {"error": "TMDB_UNAVAILABLE"}, 502


def _cached_fetch(path: str, params: dict) -> tuple[dict, int]:
    normalized = _normalize_params(params)
    cache_key = _build_cache_key(path, normalized)

    cached = CachedPayload.query.filter_by(cache_key=cache_key).first()
    if cached and not _is_expired(cached.updated_at):
        return cached.payload, 200

    payload, status = _tmdb_fetch(path, dict(normalized))
    if status == 200:
        if cached:
            cached.payload = payload
            cached.updated_at = datetime.utcnow()
        else:
            cached = CachedPayload(cache_key=cache_key, payload=payload, updated_at=datetime.utcnow())
            db.session.add(cached)
        db.session.commit()
    return payload, status


@v1_bp.get("/tmdb/trending")
def tmdb_trending():
    media_type = request.args.get("media_type", "all")
    time_window = request.args.get("time_window", "day")
    page = request.args.get("page", "1")
    params = {"page": page, **_language_param()}
    return _cached_fetch(f"/trending/{media_type}/{time_window}", params)


@v1_bp.get("/tmdb/popular")
def tmdb_popular():
    media_type = request.args.get("media_type", "movie")
    page = request.args.get("page", "1")
    params = {"page": page, **_language_param()}
    return _cached_fetch(f"/{media_type}/popular", params)


@v1_bp.get("/tmdb/now_playing")
def tmdb_now_playing():
    media_type = request.args.get("media_type", "movie")
    page = request.args.get("page", "1")
    path = "/movie/now_playing" if media_type == "movie" else "/tv/on_the_air"
    params = {"page": page, **_language_param()}
    return _cached_fetch(path, params)


@v1_bp.get("/tmdb/search")
def tmdb_search():
    query = request.args.get("query", "").strip()
    if not query:
        return {"error": "MISSING_QUERY"}, 400
    media_type = request.args.get("media_type", "multi")
    page = request.args.get("page", "1")
    params = {"query": query, "page": page, "include_adult": "false", **_language_param()}
    normalized = _normalize_params(params)
    return _tmdb_fetch(f"/search/{media_type}", normalized)


@v1_bp.get("/tmdb/tv/<int:tv_id>")
def tmdb_tv_detail(tv_id: int):
    return _cached_fetch(f"/tv/{tv_id}", _language_param())


@v1_bp.get("/tmdb/tv/<int:tv_id>/credits")
def tmdb_tv_credits(tv_id: int):
    return _cached_fetch(f"/tv/{tv_id}/credits", _language_param())


@v1_bp.get("/tmdb/tv/<int:tv_id>/videos")
def tmdb_tv_videos(tv_id: int):
    return _cached_fetch(f"/tv/{tv_id}/videos", _language_param())


@v1_bp.get("/tmdb/movie/<int:movie_id>")
def tmdb_movie_detail(movie_id: int):
    return _cached_fetch(f"/movie/{movie_id}", _language_param())


@v1_bp.get("/tmdb/movie/<int:movie_id>/credits")
def tmdb_movie_credits(movie_id: int):
    return _cached_fetch(f"/movie/{movie_id}/credits", _language_param())


@v1_bp.get("/tmdb/movie/<int:movie_id>/videos")
def tmdb_movie_videos(movie_id: int):
    return _cached_fetch(f"/movie/{movie_id}/videos", _language_param())
