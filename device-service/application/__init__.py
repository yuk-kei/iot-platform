from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.DevelopmentConfig')
    db.init_app(app)

    with app.app_context():
        from .routes import devices_blueprint

        app.register_blueprint(devices_blueprint)

    return app
