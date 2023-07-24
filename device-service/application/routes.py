import time, uuid

from .models import Device, db
from flask import Blueprint, request, jsonify

devices_blueprint = Blueprint('devices', __name__, url_prefix="/api/devices")


@devices_blueprint.route('/test')
def hello():
    return '<h1>Home</h1>'


@devices_blueprint.route("/register", methods=['POST', 'GET'])
def check_register():
    if request.method == 'POST':
        device_id = request.json.get('device_id')
        name = request.json.get('name')
        type = request.json.get('type')
        category = request.json.get('category')
        location = request.json.get('location')
        status = request.json.get('status')
        ip_address = request.json.get('ip_address')
        port = request.json.get('port')
        if not device_id:
            device_id = next_short_id()
            new_device = Device(id=device_id, name=name, type=type, category=category, location=location, status=status,
                                ip_address=ip_address, port=port)
            db.session.add(new_device)
            db.session.commit()
            return jsonify({'device_id': device_id}), 201
        else:
            device = Device.query.get(device_id)
            if device:
                return jsonify({'message': 'Device already registered.'}), 200
            else:
                return jsonify({'message': 'Device ID not found in database.'}), 404
    elif request.method == 'GET':
        # Logic for handling GET requests
        devices = Device.query.all()
        device_list = [{'device_id': device.id, 'name': device.name, 'type': device.type, 'location': device.location,
                        'category': device.category, 'status': device.status, 'ip_address': device.ip_address,
                        'port': device.port} for device in devices]
        return jsonify(device_list), 200


@devices_blueprint.route("/delete")
def delete_device():
    device_id = request.json.get('device_id')
    device = Device.query.get(device_id)
    if device:
        db.session.delete(device)
        db.session.commit()
        return jsonify({'message': 'Device deleted.'}), 200
    else:
        return jsonify({'message': 'Device ID not found in database.'}), 404


@devices_blueprint.route("/update")
def update_device():
    device_id = request.json.get('device_id')
    device = Device.query.get(device_id)
    if device:
        device.name = request.json.get('name')
        device.type = request.json.get('type')
        device.location = request.json.get('location')
        device.status = request.json.get('status')
        device.ip_address = request.json.get('ip_address')
        device.port = request.json.get('port')
        db.session.commit()
        return jsonify({'message': 'Device updated.'}), 200
    else:
        return jsonify({'message': 'Device ID not found in database.'}), 404


@devices_blueprint.route("/get_type")
def get_type():
    type = request.json.get('type')
    devices = Device.query.filter_by(type=type).all()
    device_list = [{'device_id': device.id, 'name': device.name, 'type': device.type, 'location': device.location,
                    'status': device.status, 'ip_address': device.ip_address} for device in devices]
    return jsonify(device_list), 200


@devices_blueprint.route("/filter_by", methods=['POST', 'GET'])
def filter_by_field():
    # Get the field name and value from the request
    field_name = request.json.get('field_name')
    field_value = request.json.get('field_value')
    # Check if the field is present in the Device model
    if hasattr(Device, field_name):
        # Construct the filter dynamically based on the field name and value
        filter_kwargs = {field_name: field_value}
        devices = Device.query.filter_by(**filter_kwargs).all()
        device_list = [{'device_id': device.id, 'name': device.name, 'type': device.type, 'location': device.location,
                        'status': device.status, 'ip_address': device.ip_address} for device in devices]
        return jsonify(device_list), 200
    else:
        return jsonify({'message': 'Field name not found '}), 404


def next_short_id():
    current_time_str = str(int(time.time()))
    uid = uuid.uuid4().bytes_le[:4].hex()
    return current_time_str + uid