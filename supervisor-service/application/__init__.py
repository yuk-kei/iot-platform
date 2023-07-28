from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.DevelopmentConfig')

    with app.app_context():
        from .routes import control_blueprint

        app.register_blueprint(control_blueprint)

    return app
