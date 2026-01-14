import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")
    TMDB_LANGUAGE = os.getenv("TMDB_LANGUAGE", "zh-CN")
    TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    TMDB_CACHE_ENABLED = os.getenv("TMDB_CACHE_ENABLED", "true").lower() in ("1", "true", "yes")
