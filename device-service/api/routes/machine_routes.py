from flask import Blueprint, jsonify, request
from api.dao.machine_dao import MachineDAO
from api.schemas.machine_schema import MachineSchema, SingleOverviewSchema, ResultSchema, AllMachineSchema, SensorsForMachine, KeySensorsSchema
machine_blueprint = Blueprint('machine_routes', __name__, url_prefix='/api/v1/machine')
from apifairy import body, response


machine_info = MachineSchema()
single_overview = SingleOverviewSchema()
result = ResultSchema()
all_machines = AllMachineSchema()
sensors_machine = SensorsForMachine()
key_sensors_schema = KeySensorsSchema(many=True)

@machine_blueprint.route('/<machine_identifier>', methods=['GET'])
@response(machine_info, 200)
def get_machine(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    machine = MachineDAO.get_single(machine_identifier)
    return machine


@machine_blueprint.route('/<machine_identifier>/overview', methods=['GET'])
@response(single_overview, 200)
def get_machine_overview(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    machine_overview = MachineDAO.get_single_overview(machine_identifier)
    return machine_overview


@machine_blueprint.route('/<machine_identifier>/overview', methods=['PUT'])
@response(single_overview, 200)
def update_machine_overview(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    update_data = request.json
    machine_overview = MachineDAO.update_machine_overview(machine_identifier, update_data)
    return machine_overview


@machine_blueprint.route('/<machine_identifier>/result', methods=['GET'])
@response(result, 200)
def get_machine_result(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    machine_result = MachineDAO.get_single_result(machine_identifier)
    return machine_result


@machine_blueprint.route('/<machine_identifier>/result', methods=['PUT'])
@response(result, 200)
def update_machine_result(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    update_data = request.json
    machine_result = MachineDAO.update_machine_result(machine_identifier, update_data)
    return machine_result


@machine_blueprint.route('/', methods=['GET'])
@response(all_machines, 200)
def get_all_machines():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=50, type=int)

    machines, total_pages, total = MachineDAO.get_all(page, per_page)
    # machines, total_pages, total = MachineService.get_all(page, per_page)
    return {
        'machines': [m.to_dict() for m in machines],
        'total': total,
        'pages': total_pages,
        'current_page': page
    }


@machine_blueprint.route('/<machine_identifier>/sensors', methods=['GET'])
@response(sensors_machine, 200)
def get_sensors_from_machine(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=50, type=int)
    sensors, total = MachineDAO.get_sensors(machine_identifier, page, per_page)

    return {'sensors': [s.to_dict()
                                for s in sensors],
                    'total': total}


@machine_blueprint.route('/<machine_identifier>/key-sensors', methods=['GET'])
@response(key_sensors_schema, 200)
def get_key_sensors_from_machine(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=50, type=int)
    key_sensors, total = MachineDAO.get_key_sensors(machine_identifier, page, per_page)
    # key_sensors, total = MachineService.get_key_sensors(machine_id, page, per_page)

    return key_sensors


@machine_blueprint.route('/<machine_identifier>/key-info', methods=['GET'])
@response(key_sensors_schema, 200)
def get_key_info_from_machine(machine_identifier):
    try:
        # Attempt to convert to an integer
        machine_identifier = int(machine_identifier)
    except ValueError:
        machine_identifier = machine_identifier

    key_info = MachineDAO.get_key_info(machine_identifier)
    return key_info
