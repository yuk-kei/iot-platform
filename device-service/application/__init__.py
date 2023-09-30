from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    @app.after_request
    def add_security_headers(response):
        """
        The add_security_headers function adds security headers to the response.
        Currently useless but can be used to add security headers to the response.

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

    with app.app_context():
        from .routes import devices_blueprint

        app.register_blueprint(devices_blueprint)

    return app
