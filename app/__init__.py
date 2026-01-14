from flask import Flask, send_from_directory
from dotenv import load_dotenv

from .config import Config
from .extensions import db, migrate, jwt
from .api.v1 import v1_bp

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(v1_bp, url_prefix="/api/v1")

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/")
    def home():
        return send_from_directory("static", "home.html")

    @app.get("/home")
    def home_page():
        return send_from_directory("static", "home.html")

    @app.get("/search")
    def search_page():
        return send_from_directory("static", "search.html")

    @app.get("/series")
    @app.get("/series/<int:series_id>")
    def series_page(series_id: int | None = None):
        return send_from_directory("static", "series.html")

    @app.get("/movie")
    @app.get("/movie/<int:movie_id>")
    def movie_page(movie_id: int | None = None):
        return send_from_directory("static", "movie.html")

    @app.get("/login")
    def login_page():
        return send_from_directory("static", "login.html")

    @app.get("/register")
    def register_page():
        return send_from_directory("static", "register.html")

    return app
