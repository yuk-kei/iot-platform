from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.DevelopmentConfig')
    db.init_app(app)

    with app.app_context():
        from .routes import control_blueprint

        app.register_blueprint(control_blueprint)

    return app