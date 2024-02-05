import time, uuid

from ..models.lab import Lab
from ..dao.lab_dao import LabDAO
from flask import Blueprint, request, jsonify
from ..schemas.lab_schema import LabDetailsSchema
from apifairy import body, response

lab_blueprint = Blueprint('lab', __name__, url_prefix="/api/v1/lab")
detail_schema = LabDetailsSchema(many=True)

@lab_blueprint.route('<lab_identifier>/get-all-info', methods=['GET'])
@response(detail_schema, 200)
def get_lab_key_info(lab_identifier):
    try:
        # Attempt to convert to an integer
        lab_identifier = int(lab_identifier)
    except ValueError:
        lab_identifier = lab_identifier

    lab_info = LabDAO.get_key_info_from_lab(lab_identifier)
    return lab_info

