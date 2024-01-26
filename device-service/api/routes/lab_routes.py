import time, uuid

from ..models.lab import Lab
from ..dao.lab_dao import LabDAO
from flask import Blueprint, request, jsonify

lab_blueprint = Blueprint('lab', __name__, url_prefix="/api/v1/lab")


@lab_blueprint.route('<lab_identifier>/get-all-info', methods=['GET'])
def get_lab_key_info(lab_identifier):
    try:
        # Attempt to convert to an integer
        lab_identifier = int(lab_identifier)
    except ValueError:
        lab_identifier = lab_identifier

    lab_info = LabDAO.get_key_info_from_lab(lab_identifier)
    return jsonify(lab_info), 200

