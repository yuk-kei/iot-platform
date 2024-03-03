from flask import Blueprint, request, jsonify
from .actions import DeviceController
from .models import DeviceInfo
"""
Device Control API Endpoints

This module defines a set of api that serve as the API endpoints for system control operations.
It enables clients to interact with devices by providing functionalities such as pausing,
resuming, and changing the rate of a device. Each route corresponds to a specific action
and requires certain parameters, like device ID, port, and IP address, to execute the action.

The module leverages a `DeviceController` class from the `actions` module to perform these
operations and uses the `DeviceInfo` class from the `models` module to structure the data.

Future will be to add the capability to control other part of the system, 
and supervise the condition of the system.

Routes:
- `/test`: Tests the connectivity to the API.
- `/pause`: Pause a specific device.
- `/resume`: Resume a paused device.
- `/change_rate`: Change the rate of a device.

"""
control_blueprint = Blueprint('control', __name__, url_prefix="/api/control")

device_controller = DeviceController()


@control_blueprint.route('/test')
def hello():
    """
    Tests the connectivity to the API.

    :return: A message confirming successful connection.
    :doc-author: Yukkei
    """
    return '<h1>Connection Success</h1>'


@control_blueprint.route("/pause", methods=['POST'])
def pause_device():
    """
    Pause a device given its ID, port, and IP address.

    :return: The result of the pause action and a corresponding status code.
    :doc-author: Yukkei
    """
    device_id = request.json.get('device_id')
    device_port = request.json.get('port')
    device_ip = request.json.get('ip_address')
    device_info = DeviceInfo(device_id, device_ip, device_port)

    result, status_code = device_controller.pause(device_info)
    return result, status_code


@control_blueprint.route("/resume", methods=['POST'])
def resume_device():
    """
    Resume a paused device given its ID, port, and IP address.

    :return: The result of the resume action and a corresponding status code.
    :doc-author: Yukkei
    """
    device_id = request.json.get('device_id')
    device_port = request.json.get('port')
    device_ip = request.json.get('ip_address')
    device_info = DeviceInfo(device_id, device_ip, device_port)

    result, status_code = device_controller.resume(device_info)
    return result, status_code


@control_blueprint.route("/change-rate", methods=['POST'])
def change_rate():
    """
    Change the rate of a device given its ID, port, IP address, and the desired rate.

    :return: The result of the rate change action and a corresponding status code.
    :doc-author: Yukkei
    """
    device_id = request.json.get('device_id')
    device_port = request.json.get('port')
    device_ip = request.json.get('ip_address')
    device_info = DeviceInfo(device_id, device_ip, device_port)

    rate = request.json.get('rate')
    result, status_code = device_controller.change_rate(device_info, rate)
    return result, status_code
