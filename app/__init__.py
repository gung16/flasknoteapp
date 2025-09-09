from flask import Flask
from .extensions import db, migrate, cache, limiter
from .routes import notes_bp

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 60

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    limiter.init_app(app)

    # register blueprints
    app.register_blueprint(notes_bp)

    # custom extension (X-Request-ID header)
    @app.after_request
    def add_request_id(response):
        import uuid
        response.headers["X-Request-ID"] = str(uuid.uuid4())
        return response

    return app
