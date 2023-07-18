from flask import request, jsonify
import time, uuid

from app import app
from data_handler import search_data_influxdb
from model import Device, db


@app.route('/hello')
def hello():
    return '<h1>Home</h1>'


@app.route("/api/devices/register", methods=['POST', 'GET'])
def check_register():
    if request.method == 'POST':
        device_id = request.json.get('device_id')
        name = request.json.get('name')
        type = request.json.get('type')
        location = request.json.get('location')
        status = request.json.get('status')
        ip_address = request.json.get('ip_address')
        port = request.json.get('port')
        if not device_id:
            device_id = next_id()
            new_device = Device(id=device_id, name=name, type=type, location=location, status=status,
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
                        'status': device.status, 'ip_address': device.ip_address} for device in devices]
        return jsonify(device_list), 200


@app.route("/api/devices/delete")
def delete_device():
    device_id = request.json.get('device_id')
    device = Device.query.get(device_id)
    if device:
        db.session.delete(device)
        db.session.commit()
        return jsonify({'message': 'Device deleted.'}), 200
    else:
        return jsonify({'message': 'Device ID not found in database.'}), 404


@app.route("/api/devices/update")
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


@app.route("/api/devices/get_type")
def get_type():
    type = request.json.get('type')
    devices = Device.query.filter_by(type=type).all()
    device_list = [{'device_id': device.id, 'name': device.name, 'type': device.type, 'location': device.location,
                    'status': device.status, 'ip_address': device.ip_address} for device in devices]
    return jsonify(device_list), 200


@app.route("/api/devices/filter_by")
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


@app.route("/api/data/get_data")
def get_data():
    record = search_data_influxdb("measurement", "Device 1", "-1h")
    return record.to_json(indent=2)


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)
