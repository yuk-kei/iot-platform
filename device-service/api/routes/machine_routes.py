import time, uuid

from ..models.machine import Machine
from ..dao.machine_dao import MachineDAO
from flask import Blueprint, request, jsonify

machine_blueprint = Blueprint('machine', __name__, url_prefix="/api/machine")


@machine_blueprint.route('/test')
def hello():
   """
    Test Endpoint
    This route is used to check if the device-related endpoints are accessible and functioning.

    :return: A simple greeting string confirming the accessibility of the endpoint.
    """
   return '<h1>Machine Home</h1>'


@machine_blueprint.route('/create', methods=['POST', 'GET', 'PUT'])
def create_machine():
   data = request.get_json()
   new_machine = MachineDAO.create_machine(data.get("machine_uuid"), data.get('name'), data.get('type'),
                                           data.get('vendor'), data.get('year'), data.get('lab_id'))
   return jsonify({'message': f'Machine {new_machine.name} created successfully'}), 201


@machine_blueprint.route('/read')
def read_machine():
   machine_id = request.json.get('machine_id')
   current_machine = MachineDAO.read_machine(machine_id)
   machine_list = [{'machine_id': current_machine.machine_id, 'machine_uuid': current_machine.machine_uuid,
                    'name': current_machine.name, 'type': current_machine.type,
                    'vendor': current_machine.vendor, 'year': current_machine.year,
                    'lab_id': current_machine.lab_id}]
   return jsonify(machine_list), 200


@machine_blueprint.route('/delete', methods=['POST'])
def delete_machine():
   machine_id = request.json.get('machine_id')
   deleted_machine = MachineDAO.delete_machine(machine_id)
   if deleted_machine:
      return jsonify({'message': f'Machine {deleted_machine.name} deleted successfully'})
   else:
      return jsonify({'message': 'Machine ID not found in database.'}), 404


@machine_blueprint.route('/update/<machine_id>', methods=['PUT'])
def update_machine(machine_id):
   data = request.get_json()
   updated_machine = MachineDAO.update_machine(machine_id, data)
   if updated_machine:
      return jsonify({'message': f'Machine {updated_machine.name} updated successfully'})
   else:
      return jsonify({'message': 'Machine ID not found in database.'}), 404
