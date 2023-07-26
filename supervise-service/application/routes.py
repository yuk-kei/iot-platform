from flask import Blueprint, request, jsonify

control_blueprint = Blueprint('control', __name__, url_prefix="/api/control")


@control_blueprint.route('/test')
def hello():
    return '<h1>Connection Success</h1>'
