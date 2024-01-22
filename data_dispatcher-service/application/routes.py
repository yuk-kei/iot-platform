import io

from flask import Blueprint, request, jsonify, Response, current_app

from .data_handler import InfluxDataHandler
from .kafka_handler import KafkaService, KafkaStreamHandler

"""
    Data Blueprint
    This blueprint is responsible for handling data requests.
    The blueprint is registered in the app.py file.
    All routes in this file are prefixed with /api/data

    The blueprint is responsible for handling all requests related to the data.
    This includes:
        - Querying data from the influxdb
        - Streaming large data from the influxdb
        - Querying latest data from kafka
        - Streaming data from the kafka

    The blueprint uses the data_handler.py file to interact with the influxdb.
    The blueprint uses the kafka_handler.py file to interact with the kafka.
"""

data_blueprint = Blueprint('data', __name__, url_prefix="/api/data")

influx_handler = InfluxDataHandler()
kafka_service = KafkaService()
# kafka_service.subscribe(['sensor_data'])
kafka_handler = KafkaStreamHandler()
kafka_handler.start()


@data_blueprint.route('/test')
def hello():
    """
    Test the connection to the data blueprint

    :return: A string
    :doc-author: Yukkei
    """
    return '<h1>Connection Success</h1>'


@data_blueprint.route("/query", methods=['POST'])
def query_influx_data():
    """
    The query_influx_data function is a POST request that takes in the following parameters:
    field_name - The name of the field to be queried.
    field_value - The value of the specified field to be queried.
    start_time - A string representing a time in UTC format (YYYY-MM-DDTHH:MM:SSZ).
    This will serve as the starting point for our query.
    If no end time is provided, this will also serve as our ending point for our query.
    If an end time is provided, then we will search from start_time until current time.

    :return: A json response containing the queried data.
    :doc-author: Yukkei
    """
    if request.method == 'POST':
        current_app.logger.info(f"Received a POST request: {request.get_json()}")
        field_name = request.json.get('field_name')
        field_value = request.json.get('field_value')
        start_time = request.json.get('start_time')
        end_time = request.json.get('end_time')
        frequency = request.json.get('frequency', None)

        result = influx_handler.search_data_influxdb(field_name, field_value, start_time, end_time, frequency)
        result = influx_handler.format_results(result)

        return jsonify(result), 200


@data_blueprint.route("/query/latest", methods=['POST'])
def query_latest_data():
    """
    The query_influx_data function is a POST request that takes in the following parameters:
    field_name - The name of the field to be queried.
    field_value - The value of the specified field to be queried.
    start_time - A string representing a time in UTC format (YYYY-MM-DDTHH:MM:SSZ).
    This will serve as the starting point for our query.
    If no end time is provided, this will also serve as our ending point for our query.
    If an end time is provided, then we will search from start_time until current time.

    :return: A json response containing the queried data.
    :doc-author: Yukkei
    """
    if request.method == 'POST':
        current_app.logger.info(f"Received a POST request: {request.get_json()}")
        field_name = request.json.get('field_name')
        field_value = request.json.get('field_value')
        start_time = request.json.get('start_time')
        end_time = request.json.get('end_time')

        result = influx_handler.search_data_influxdb(field_name, field_value, start_time, end_time, is_latest=True)
        result = influx_handler.format_results(result)

        return jsonify(result), 200


@data_blueprint.route("/last_min/<string:field_name>")
def query_last_min(field_name):
    """
    Not recommended to use this function. Use the query_influx_data function instead.
    Query the last minute of data from single sensor.
    The function uses the search_data_influxdb function to query InfluxDB for a single sensor
    with a timestamp within one minute of now, and then returns those records as JSON.

    :param field_name: Specify the field name of the measurement
    :return: The last minute of data in json format
    :doc-author: Yukkei
    """
    record = influx_handler.search_data_influxdb("measurement", field_name, "-1m")

    return record.to_json()


@data_blueprint.route("/csv", methods=['GET', 'POST'])
def get_csv():
    """
    The get_csv function is a GET request that takes in the following parameters:
    field_name - The name of the field to be queried.
    field_value - The value of the specified field to be queried.
    start_time - A string representing a time in UTC format (YYYY-MM-DDTHH:MM:SSZ).
    This will serve as the starting point for our query.
    If no end time is provided, this will also serve as our ending point for our query.
    If an end time is provided, then we will search from start_time until current time.

    :return: A csv file containing the queried data.
    :doc-author: Yukkei
    """
    if request.method == 'POST':
        field_name = request.json.get('field_name', default="measurement")
        field_value = request.json.get('field_value')
        start_time = request.json.get('start_time')
        end_time = request.json.get('end_time', default="-0s")
        frequency = request.json.get('frequency', default=None)
        iso_format_str = request.args.get('iso_format', default='False')

    elif request.method == 'GET':
        field_name = request.args.get('field_name', default="measurement")
        field_value = request.args.get('field_value')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time', default="-0s")
        frequency = request.args.get('frequency', default=None)
        iso_format_str = request.args.get('iso_format', default='False')
    else:
        return jsonify({'message': 'Invalid request method'}), 400

    iso_format = iso_format_str.lower() == 'true'
    result = influx_handler.search_data_influxdb(field_name, field_value, start_time, end_time, frequency)
    format_result = influx_handler.format_results(result, iso_format=iso_format)
    df = influx_handler.to_csv(format_result)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    # Seek to start
    buffer.seek(0)
    return Response(buffer.getvalue(), mimetype="text/csv",
                    headers={"Content-disposition": "attachment; filename=data.csv"})


@data_blueprint.route("/influx_query", methods=['POST'])
def execute_query():
    """
    In danger of query injection. Not recommended to use in client side,
    keeping for testing or special use case.

    :return: The result of the query
    :doc-author: Yukkei
    """
    query = request.json.get('query', None)
    current_app.logger.info(f"Received a POST request: {request.get_json()}")
    result = influx_handler.query_measurements(query)
    result = influx_handler.format_results(result)
    return jsonify(result), 200


@data_blueprint.route("/large_data", methods=['POST'])
def query_large_data():
    """
    The query_large_data function is used to query large data sets from the InfluxDB database.
    The function takes in a field_name, field_value, start_time and end_time as parameters.
    It then queries the InfluxDB database for all records that match these parameters
    and returns as a stream of data.

    :return: A stream of data
    :doc-author: Yukkei
    """
    field_name = request.json.get('field_name')
    field_value = request.json.get('field_value')
    start_time = request.json.get('start_time')
    end_time = request.json.get('end_time')

    return Response(influx_handler.query_large_data(field_name, field_value, start_time, end_time),
                    mimetype='text/event-stream')


@data_blueprint.route('/influx_stream', methods=['POST'])
def influx_query_loop():
    """
    A REST endpoint that allows the user to query the InfluxDB database for a specific field name and value.
    The function returns an event stream of data from the database, which can be
    used by a front-end api to display real-time data.

    :return: A stream of data from the database
    :doc-author: Yukkei
    """
    field_name = request.json.get('field_name')
    field_value = request.json.get('field_value')
    interval = request.json.get('interval', default=3)
    rate = request.json.get('rate', default=3)

    return Response(influx_handler.stream_data(field_name, field_value, time_interval=interval, rate=rate),
                    mimetype='text/event-stream')


@data_blueprint.route('/kafka_stream/start', methods=['GET'])
def start_stream_endpoint():
    """
    Starts a thread that listens to the Kafka topic 'sensor_data' and
    stores the data in a global variable. The function returns an HTTP response with status code 200 if
    successful, or 500 otherwise.

    :return: A dictionary with a key of status
    :doc-author: Yukkei
    """
    global kafka_service
    global kafka_handler

    if kafka_service is None:
        kafka_service = KafkaService()
        kafka_service.subscribe(['sensor_data', 'ml_result'])

    if not kafka_handler or not kafka_handler.running:
        kafka_handler = KafkaStreamHandler(kafka_service)
        print("starting a thread")
        kafka_handler.start()
        kafka_handler.running = True

        return {'status': 'Stream started'}
    else:
        return {'status': 'Stream already running'}


@data_blueprint.route('/kafka_stream/latest/', methods=['GET'])
def get_latest_data_all():
    """
    Get the latest data for all sensors.
        ---
        tags:
          - Data Retrieval Functions

    :return: The latest data for all the sensors in the kafka stream
    :doc-author: Yukkei
    """
    global kafka_service
    global kafka_handler

    if not kafka_handler.running:
        return {'status': 'No stream running'}

    message = kafka_handler.get_latest_data_for_all()
    return message


@data_blueprint.route('/kafka_stream/stop', methods=['GET'])
def stop_stream_endpoint():
    """
    Stop the service that could get the latest data from the kafka stream.
        ---
        tags: [stream]
        responses:
            200:  # HTTP status code 200 indicates success! :)
                description: Stream stopped successfully.

    :return: A dictionary with a status key
    :doc-author: Yukkei
    """
    global kafka_service
    global kafka_handler
    if kafka_handler.running:
        kafka_handler.stop()
        kafka_handler.running = False
        return {'status': 'Stream stopped'}
    else:
        return {'status': 'Stream already stopped'}


@data_blueprint.route('/kafka_stream/status', methods=['GET'])
def stream_status_endpoint():
    """
    Check whether we can retrieve data from the kafka stream.
        ---
        tags: [stream]
        responses:
            200:
                description: Returns a JSON object with the status of the stream handler.

    :return: A dictionary with the status of the stream
    :doc-author: Yukkei
    """
    global kafka_service
    global kafka_handler
    if kafka_handler.running:
        return {'status': 'Stream running'}
    else:
        return {'status': 'Stream stopped'}


@data_blueprint.route('/kafka_stream/latest/<string:device_name>', methods=['GET'])
def get_latest_data(device_name):
    """
    The get_latest_data function returns the latest data for a given device.
        Args:
            device_name (str): The name of the device to get data from.

    :param device_name: Get the latest data for a specific device
    :return: The latest data for a device
    :doc-author: Yukkei
    """
    global kafka_service
    global kafka_handler

    if not kafka_handler.running:
        return {'status': 'No stream running'}

    if device_name in kafka_handler.data and device_name in kafka_handler.flag:
        message = kafka_handler.get_latest_data_for_single(str(device_name))
        return message, 200
    return {'status': 'Device not ready'}, 404


@data_blueprint.route('/kafka_stream/<device_name>', methods=['GET'])
def subscribe_to_device(device_name):
    """
    This allows client to get the data stream of a single device.
    The function takes in the name of the device as an argument and returns a response object containing
    information about whether there is currently an active stream running, and if so,
    it will stream the latest data from that particular device.

    It also takes in an optional argument called frequency, which specifies the frequency of the data stream.
    If no frequency is specified, the default frequency is 0,
    which means that the stream will be sampling base on the rate of the data being sent to the kafka.
    If the data rate is too high, it is recommended to specify a frequency to down sample the stream.

    :param device_name: Specify the device to subscribe to
    :return: A response that contains the stream of data
    :doc-author: Yukkei
    """
    global kafka_service
    global kafka_handler
    frequency = int(request.args.get('frequency', default=0))
    if not kafka_handler.running:
        return {'status': 'No stream running'}

    current_app.logger.info(f"Subscribing to {device_name} with frequency {frequency}")
    response = Response(kafka_handler.get_latest_data_stream(device_name, frequency), content_type='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'

    return response
