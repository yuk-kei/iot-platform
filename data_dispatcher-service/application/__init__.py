from flask import Flask
from flask_cors import CORS
import gevent.monkey
gevent.monkey.patch_all()

def create_app():
    """
    The create_app function wraps the creation of a new Flask api,

    :return: The flask app object
    :doc-author: Yukkei
    """
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

    CORS(app)  # Allow CORS for all domains on all routes
    app.config.from_object('config.DevelopmentConfig')

    from .routes import data_blueprint
    app.register_blueprint(data_blueprint)

    # from .sio_routes import kafka_blueprint, socketio
    # app.register_blueprint(kafka_blueprint)
    #
    # socketio.init_app(app)

    return app
