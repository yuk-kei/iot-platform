from flask import Blueprint, request, jsonify

from .data_handler import InfluxDataHandler

data_blueprint = Blueprint('data', __name__, url_prefix="/api/data")

influx_handler = InfluxDataHandler()


@data_blueprint.route('/test')
def hello():
    return '<h1>Connection Success</h1>'


@data_blueprint.route("/query", methods=['POST'])
def query_influx_data():
    if request.method == 'POST':
        field_name = request.json.get('field_name')
        field_value = request.json.get('field_value')
        start_time = request.json.get('start_time')
        end_time = request.json.get('end_time')

        result = influx_handler.search_data_influxdb(field_name, field_value, start_time, end_time)
        return result.to_json(), 200


@data_blueprint.route("/last_min/<string:field_name>")
def query_last_min(field_name):
    record = influx_handler.search_data_influxdb("measurement", field_name, "-1m")

    return record.to_json()


@data_blueprint.route("/influx_query", methods=['POST'])
def execute_query():
    query = request.json.get('query', None)
    print(query)
    result = influx_handler.query_measurements(query)
    return result.to_json(), 200
