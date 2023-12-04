import time, uuid

from ..models.sensor import Sensor
from ..dao.sensor_dao import SensorDAO
from flask import Blueprint, request, jsonify

sensor_blueprint = Blueprint('sensor', __name__, url_prefix="/api/sensor")


@sensor_blueprint.route('/test')
def hello():
   """
    Test Endpoint
    This route is used to check if the device-related endpoints are accessible and functioning.

    :return: A simple greeting string confirming the accessibility of the endpoint.
    """
   return '<h1>Sensor Home</h1>'


@sensor_blueprint.route('/create', methods=['POST', 'GET', 'PUT'])
def create_sensor():
   data = request.get_json()
   new_sensor = SensorDAO.create_sensor(data.get('sensor_uuid'),data.get('name'), data.get('category'), data.get('sensor_type'),
                                        data.get('sensor_vendor'), data.get('vendor_pid'), data.get('chip'),
                                        data.get('rpi_id'))
   return jsonify({'message': f'Sensor {new_sensor.name} created successfully'}), 201

@sensor_blueprint.route('/read')
def read_sensor():
   sensor_id = request.json.get('sensor_id')
   current_sensor = SensorDAO.read_sensor(sensor_id)
   sensor_list = [{'sensor_id': current_sensor.sensor_id, 'sensor_uuid': current_sensor.sensor_uuid,
                   'name': current_sensor.name, 'category': current_sensor.category,
                   'sensor_type': current_sensor.sensor_type, 'sensor_vendor': current_sensor.sensor_vendor,
                   'vendor_pid': current_sensor.vendor_pid, 'chip': current_sensor.chip,
                   'rpi_id': current_sensor.rpi_id, 'is_key_sensor': current_sensor.is_key_sensor}]
   return jsonify(sensor_list), 200



@sensor_blueprint.route('/delete', methods=['POST'])
def delete_sensor():
   sensor_id = request.json.get('sensor_id')
   deleted_sensor = SensorDAO.delete_sensor(sensor_id)
   if deleted_sensor:
      return jsonify({'message': f'Sensor {deleted_sensor.name} deleted successfully'})
   else:
      return jsonify({'message': 'Sensor ID not found in database.'}), 404

@sensor_blueprint.route('/update/<sensor_id>', methods=['PUT'])
def update_sensor(sensor_id):
   data = request.get_json()
   updated_sensor = SensorDAO.update_sensor(sensor_id, data)
   if updated_sensor:
      return jsonify({'message': f'Sensor {updated_sensor.name} updated successfully'})
   else:
      return jsonify({'message': 'Sensor ID not found in database.'}), 404

