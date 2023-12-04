import time, uuid

from ..models.lab import Lab
from ..dao.lab_dao import LabDAO
from flask import Blueprint, request, jsonify

lab_blueprint = Blueprint('lab', __name__, url_prefix="/api/lab")


@lab_blueprint.route('/test')
def hello():
   """
    Test Endpoint
    This route is used to check if the device-related endpoints are accessible and functioning.

    :return: A simple greeting string confirming the accessibility of the endpoint.
    """
   return '<h1>Lab Home</h1>'


@lab_blueprint.route('/create', methods=['POST', 'GET', 'PUT'])
def create_lab():
   data = request.get_json()
   new_lab = LabDAO.create_lab(data.get('name'), data.get('type'))
   return jsonify({'message': f'Lab {new_lab.name} created successfully'}), 201


@lab_blueprint.route('/read')
def read_lab():
   lab_id = request.json.get('lab_id')
   current_lab = LabDAO.read_lab(lab_id)
   lab_list = [{'lab_id': current_lab.lab_id,'name': current_lab.name, 'type': current_lab.type}]
   return jsonify(lab_list), 200


@lab_blueprint.route('/delete', methods=['POST'])
def delete_lab():
   lab_id = request.json.get('lab_id')
   deleted_lab = LabDAO.delete_lab(lab_id)
   if deleted_lab:
      return jsonify({'message': f'Lab {deleted_lab.name} deleted successfully'})
   else:
      return jsonify({'message': 'Lab ID not found in database.'}), 404


@lab_blueprint.route('/update/<lab_id>', methods=['PUT'])
def update_lab(lab_id):
   data = request.get_json()
   updated_lab = LabDAO.update_lab(lab_id, data)
   if updated_lab:
      return jsonify({'message': f'Lab {updated_lab.name} updated successfully'})
   else:
      return jsonify({'message': 'Lab ID not found in database.'}), 404
