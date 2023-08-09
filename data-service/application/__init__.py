from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # If you want all HTTP converted to HTTPS
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response

    CORS(app)
    app.config.from_object('config.DevelopmentConfig')

    from .routes import data_blueprint
    app.register_blueprint(data_blueprint)

    from .sio_routes import kafka_blueprint
    app.register_blueprint(kafka_blueprint)

    return app
