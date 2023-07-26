from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.DevelopmentConfig')

    from .routes import data_blueprint
    app.register_blueprint(data_blueprint)

    return app
