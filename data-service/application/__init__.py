from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    from .routes import data_blueprint
    app.register_blueprint(data_blueprint)

    return app
