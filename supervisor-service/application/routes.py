from flask import Blueprint, request, jsonify
from .actions import DeviceController
from .models import DeviceInfo

control_blueprint = Blueprint('control', __name__, url_prefix="/api/control")

device_controller = DeviceController()


@control_blueprint.route('/test')
def hello():
    return '<h1>Connection Success</h1>'


@control_blueprint.route("/pause", methods=['POST'])
def pause_device():
    device_id = request.json.get('device_id')
    device_port = request.json.get('port')
    device_ip = request.json.get('ip_address')
    device_info = DeviceInfo(device_id, device_ip, device_port)

    result, status_code = device_controller.pause(device_info)
    return result, status_code


@control_blueprint.route("/resume", methods=['POST'])
def resume_device():
    device_id = request.json.get('device_id')
    device_port = request.json.get('port')
    device_ip = request.json.get('ip_address')
    device_info = DeviceInfo(device_id, device_ip, device_port)

    result, status_code = device_controller.resume(device_info)
    return result, status_code


@control_blueprint.route("/change_rate", methods=['POST'])
def change_rate():
    device_id = request.json.get('device_id')
    device_port = request.json.get('port')
    device_ip = request.json.get('ip_address')
    device_info = DeviceInfo(device_id, device_ip, device_port)

    rate = request.json.get('rate')
    result, status_code = device_controller.change_rate(device_info, rate)
    return result, status_code
