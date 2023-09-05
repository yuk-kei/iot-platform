from flask import Blueprint, request, jsonify, Response


from .data_handler import InfluxDataHandler
from .kafka_handler import KafkaService

data_blueprint = Blueprint('data', __name__, url_prefix="/api/data")

influx_handler = InfluxDataHandler()
states = {"is_streaming": True}


@data_blueprint.route('/test')
def hello():
    return '<h1>Connection Success</h1>'


@data_blueprint.route("/query", methods=['POST'])
def query_influx_data():
    if request.method == 'POST':
        print(request.get_json())
        field_name = request.json.get('field_name')
        field_value = request.json.get('field_value')
        start_time = request.json.get('start_time')
        end_time = request.json.get('end_time')
        if request.json.get('frequency') is not None:
            frequency = request.json.get('frequency')
            result = influx_handler.search_data_influxdb(field_name, field_value, start_time, end_time, frequency)
        else:
            result = influx_handler.search_data_influxdb(field_name, field_value, start_time, end_time)
        result = influx_handler.to_dict(result)
        return jsonify(result), 200


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


@data_blueprint.route("/formatted", methods=['POST'])
def query_data_frame():
    query = request.json.get('query', None)
    print(query)
    result = influx_handler.query_measurements(query)
    result = influx_handler.to_dict(result)
    return jsonify(result), 200


@data_blueprint.route("/large_data", methods=['POST'])
def query_large_data():
    field_name = request.json.get('field_name')
    field_value = request.json.get('field_value')
    start_time = request.json.get('start_time')
    end_time = request.json.get('end_time')

    return Response(influx_handler.query_large_data(field_name, field_value, start_time, end_time),
                    mimetype='text/event-stream')


@data_blueprint.route('/influx_stream', methods=['POST'])
def influx_query_loop():
    field_name = request.json.get('field_name')
    field_value = request.json.get('field_value')

    return Response(influx_handler.stream_data(field_name, field_value, 8), mimetype='text/event-stream')


@data_blueprint.route('/kafka_stream', methods=['GET'])
def kafka_query_loop():
    kafka_service = KafkaService()
    kafka_service.subscribe(['sensor_data'])

    def kafka_stream():
        try:
            for message in kafka_service.gen_messages():

                yield message
        except GeneratorExit:  # Raised when client disconnects
            kafka_service.close()

    response = Response(kafka_stream(), content_type='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'

    return response

# @data_blueprint.teardown_request
# def close_kafka_service(exception=None):
#     kafka_service = getattr(g, 'kafka_service', None)
#     if kafka_service:
#         kafka_service.close()
