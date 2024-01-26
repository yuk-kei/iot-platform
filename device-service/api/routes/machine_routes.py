from flask import Blueprint, jsonify, request
from api.dao.machine_dao import MachineDAO

machine_blueprint = Blueprint('machine_routes', __name__, url_prefix='/api/v1/machine')


@machine_blueprint.route('/<machine_identifier>', methods=['GET'])
def get_machine(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    machine = MachineDAO.get_single(machine_identifier)
    return jsonify(machine.to_dict())


@machine_blueprint.route('/<machine_identifier>/overview', methods=['GET'])
def get_machine_overview(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    machine_overview = MachineDAO.get_single_overview(machine_identifier)
    return jsonify(machine_overview.to_dict())


@machine_blueprint.route('/<machine_identifier>/overview', methods=['PUT'])
def update_machine_overview(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    update_data = request.json
    machine_overview = MachineDAO.update_machine_overview(machine_identifier, update_data)
    return jsonify(machine_overview.to_dict())


@machine_blueprint.route('/<machine_identifier>/result', methods=['GET'])
def get_machine_result(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    machine_result = MachineDAO.get_single_result(machine_identifier)
    return jsonify(machine_result.to_dict())


@machine_blueprint.route('/<machine_identifier>/result', methods=['PUT'])
def update_machine_result(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    update_data = request.json
    machine_result = MachineDAO.update_machine_result(machine_identifier, update_data)
    return jsonify(machine_result.to_dict())


@machine_blueprint.route('/', methods=['GET'])
def get_all_machines():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    machines, total_pages, total = MachineDAO.get_all(page, per_page)
    # machines, total_pages, total = MachineService.get_all(page, per_page)
    return jsonify({
        'machines': [m.to_dict() for m in machines],
        'total': total,
        'pages': total_pages,
        'current_page': page
    })


@machine_blueprint.route('/<machine_identifier>/sensors', methods=['GET'])
def get_sensors_from_machine(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=30, type=int)
    sensors, total = MachineDAO.get_sensors(machine_identifier, page, per_page)

    return jsonify({'sensors': [s.to_dict()
                                for s in sensors],
                    'total': total})


@machine_blueprint.route('/<machine_identifier>/key_sensors', methods=['GET'])
def get_key_sensors_from_machine(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=30, type=int)
    key_sensors, total = MachineDAO.get_key_sensors(machine_identifier, page, per_page)
    # key_sensors, total = MachineService.get_key_sensors(machine_id, page, per_page)

    return jsonify(key_sensors)


@machine_blueprint.route('/<machine_identifier>/key_info', methods=['GET'])
def get_key_info_from_machine(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    key_info = MachineDAO.get_key_info(machine_identifier)
    return jsonify(key_info)
