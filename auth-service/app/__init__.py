from flask import Flask, redirect, url_for, request
# from alchemical.flask import Alchemical
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from apifairy import APIFairy
from config import config

db = SQLAlchemy()
ma = Marshmallow()
cors = CORS()
apifairy = APIFairy()


def create_app(config_class=config['testing']):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # extensions
    from app.models import models
    db.init_app(app)
    with app.app_context():
        db.create_all()
    ma.init_app(app)
    if app.config['USE_CORS']:  # pragma: no branch
        cors.init_app(app)
    apifairy.init_app(app)

    # blueprints
    from app.routes.errors import errors
    app.register_blueprint(errors)
    from app.routes.tokens import tokens
    app.register_blueprint(tokens, url_prefix='/api')

    from app.routes.users import users
    app.register_blueprint(users, url_prefix='/api')

    # define the shell context
    @app.shell_context_processor
    def shell_context():  # pragma: no cover
        ctx = {'db': db}
        for attr in dir(models):
            model = getattr(models, attr)
            if hasattr(model, '__bases__') and \
                    db.Model in getattr(model, '__bases__'):
                ctx[attr] = model
        return ctx

    @app.route('/')
    def index():  # pragma: no cover
        return redirect(url_for('apifairy.docs'))

    @app.after_request
    def after_request(response):
        # Werkzeug sometimes does not flush the request body so we do it here
        request.get_data()
        return response

    return app
