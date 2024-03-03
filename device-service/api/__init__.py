from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from apifairy import APIFairy

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
apifairy = APIFairy()

def create_app():
    app = Flask(__name__)


    @app.after_request
    def add_security_headers(response):
        """
        This function adds security headers to the response.
        Currently useless, since https is not enabled.

        :param response: Access the response object
        :return: The response object with the security headers added
        :doc-author: Trelent
        """
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # If you want all HTTP converted to HTTPS
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response

    CORS(app)
    app.config.from_object('config.DevelopmentConfig')

    db.init_app(app)
    ma.init_app(app)
    apifairy.init_app(app)
    from .routes.sensor import sensor_blueprint
    app.register_blueprint(sensor_blueprint)

    with app.app_context():
        # from .api.sensor_routes import sensor_blueprint
        from .routes.machine_routes import machine_blueprint
        from .routes.lab_routes import lab_blueprint
        # from .auth import auth_blueprint
        # app.register_blueprint(sensor_blueprint)
        app.register_blueprint(machine_blueprint)
        app.register_blueprint(lab_blueprint)
        # app.register_blueprint(auth_blueprint)
        # app.config['SWAGGER'] = {
        #     'openapi': '3.0.3'
        # }
        # swagger = Swagger(app, template_file="swagger.yml")

    return app


# import logging
# import os
# from logging.handlers import RotatingFileHandler
#
# from flask import Flask, request, current_app
# from app_config import Config
#
#
# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)
#
#     if not app.debug and not app.testing:
#
#         if app.config['LOG_TO_STDOUT']:
#             stream_handler = logging.StreamHandler()
#             stream_handler.setLevel(logging.INFO)
#             app.logger.addHandler(stream_handler)
#         else:
#             if not os.path.exists('logs'):
#                 os.mkdir('logs')
#             file_handler = RotatingFileHandler('logs/data service.log',
#                                                maxBytes=10240, backupCount=10)
#             file_handler.setFormatter(logging.Formatter(
#                 '%(asctime)s %(levelname)s: %(message)s '
#                 '[in %(pathname)s:%(lineno)d]'))
#             file_handler.setLevel(logging.INFO)
#             app.logger.addHandler(file_handler)
#
#         app.logger.setLevel(logging.INFO)
#         app.logger.info('Data service startup')
#
#     return app