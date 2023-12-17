from flask import Blueprint, jsonify, request
from ..services.machine_service import MachineService

machine_blueprint = Blueprint('machine_routes', __name__, url_prefix='/api/v1/machine')


@machine_blueprint.route('/', methods=['GET'])
def get_all_machines():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    machines, total_pages, total = MachineService.get_all(page, per_page)
    return jsonify({
        'machines': [m.to_dict() for m in machines],
        'total': total,
        'pages': total_pages,
        'current_page': page
    })


@machine_blueprint.route('/<int:machine_id>/sensors', methods=['GET'])
def get_sensors_from_machine(machine_id):
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=30, type=int)
    sensors, total = MachineService.get_sensors(machine_id, page, per_page)

    return jsonify({'sensors': [s.to_dict()
                                for s in sensors],
                    'total': total})


@machine_blueprint.route('/<int:machine_id>/key_sensors', methods=['GET'])
def get_key_sensors_from_machine(machine_id):
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=30, type=int)
    key_sensors, total = MachineService.get_key_sensors(machine_id, page, per_page)

    return jsonify(key_sensors)


@machine_blueprint.route('/<int:machine_id>/key_info', methods=['GET'])
def get_key_info_from_machine(machine_id):
    key_info = MachineService.get_key_sensor_details(machine_id)
    return jsonify(key_info)


