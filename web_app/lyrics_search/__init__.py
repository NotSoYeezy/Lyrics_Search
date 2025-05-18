import os

from flask import Flask
from .extensions import db, migrate
from .routes import bp
from .models import Song


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(bp)

    return app