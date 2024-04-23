import os

from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from apifairy import APIFairy

ma = Marshmallow()
apifairy = APIFairy()

def create_app():
    """
    The create_app function wraps the creation of a new Flask api,

    :return: The flask app object
    :doc-author: Yukkei
    """

    app = Flask(__name__)
    CORS(app)  # Allow CORS for all domains on all api
    app.config.from_object('config.DevelopmentConfig')
    apifairy.init_app(app)
    from app.routes import data_blueprint
    app.register_blueprint(data_blueprint)
    from app.api.influx_data import influx_blueprint
    app.register_blueprint(influx_blueprint)
    from app.api.kafka_data import kafka_blueprint
    app.register_blueprint(kafka_blueprint)
    return app
