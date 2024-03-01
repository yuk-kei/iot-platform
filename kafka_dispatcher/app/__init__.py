from flask import Flask
from flask_cors import CORS


def create_app():
    """
    The create_app function wraps the creation of a new Flask api,

    :return: The flask app object
    :doc-author: Yukkei
    """
    app = Flask(__name__)

    CORS(app)  # Allow CORS for all domains on all routes
    app.config.from_object('config.DevelopmentConfig')

    from .routes import kafka_blueprint
    app.register_blueprint(kafka_blueprint)

    return app
