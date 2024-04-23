import io
from datetime import datetime, timedelta

import requests

from flask import Blueprint, request, jsonify, Response, current_app, stream_with_context

from .data_handler import InfluxDataHandler
from .utils import parse_time_input


"""
    Data Blueprint
    This blueprint is responsible for handling data requests.
    The blueprint is registered in the app.py file.
    All api in this file are prefixed with /api/data

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


@data_blueprint.route('/test')
def test_connection():
    """
    Test the connection to the data blueprint

    :return: A string
    :doc-author: Yukkei
    """
    return '<h1>Connection Success</h1>'


@data_blueprint.route("/query", methods=['GET', 'POST'])
def query_influx_data():
    """
    """
    # endpoint = request.endpoint
    # remote_ip = request.remote_addr
    # print(f"Received a POST request on endpoint {endpoint} from IP {remote_ip}")
    if request.method == 'GET':
        field_name = request.args.get('field_name', 'measurement')
        field_value = request.args.get('field_value')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time', '-0s')
        frequency = request.args.get('frequency', None)
    elif request.method == 'POST':
        # current_app.logger.info(f"Received a POST request: {request.get_json()}")
        field_name = request.json.get('field_name', 'measurement')
        field_value = request.json.get('field_value')
        start_time = request.json.get('start_time')
        end_time = request.json.get('end_time', '-0s')
        frequency = request.json.get('frequency', None)
    else:
        return jsonify({'message': 'Invalid request method'}), 400

    result = influx_handler.query_as_dataframe(field_name,
                                               field_value,
                                               start_time,
                                               end_time,
                                               frequency=frequency)

    if result is None:
        return jsonify({"error": f"No data found for {field_name} in from {start_time} to {end_time} time ."}), 404

    result = influx_handler.df_to_dict(result)

    return jsonify(result), 200


@data_blueprint.route("/query/latest", methods=['POST'])
def query_latest_data():
    """
    The query_influx_data function is a POST request that takes in the following parameters:
    field_name - The name of the field to be queried.
    field_value - The value of the specified field to be queried.
    This will serve as the starting point for our query.
    If no end time is provided, this will also serve as our ending point for our query.
    If an end time is provided, then we will search from start_time until current time.

    :return: A json response containing the queried data.
    :doc-author: Yukkei
    """
    if request.method == 'GET':
        field_name = request.args.get('field_name', 'measurement')
        field_value = request.args.get('field_value')
        start_time = request.args.get('start_time', "-7d")
        end_time = request.args.get('end_time', "-0s")

    elif request.method == 'POST':
        # current_app.logger.info(f"Received a POST request: {request.get_json()}")
        field_name = request.json.get('field_name', "measurement")
        field_value = request.json.get('field_value')
        start_time = request.json.get('start_time', "-7d")
        end_time = request.json.get('end_time', "-0s")
    else:
        return jsonify({'message': 'Invalid request method'}), 400

    result = influx_handler.query_as_dataframe(field_name,
                                               field_value,
                                               start_time,
                                               end_time,
                                               is_latest=True)
    if result is None:
        return jsonify({"error": f"No data found for {field_name} in the {start_time} time ."}), 404
    result = influx_handler.df_to_dict(result)

    return jsonify(result), 200


@data_blueprint.route("/csv", methods=['GET', 'POST'])
def get_csv():
    # endpoint = request.endpoint
    # remote_ip = request.remote_addr
    # print(f"Received a POST request on endpoint {endpoint} from IP {remote_ip}")
    if request.method == 'POST':
        field_name = request.json.get('field_name', "measurement")
        field_value = request.json.get('field_value')
        start_time = request.json.get('start_time')
        end_time = request.json.get('end_time', "-0s")
        frequency = request.json.get('frequency', None)
        iso_format_str = request.args.get('iso_format', 'False')

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
    df = influx_handler.query_as_dataframe(field_name=field_name,
                                           field_value=field_value,
                                           start_time_str=start_time,
                                           frequency=frequency,
                                           end_time_str=end_time)
    if df is None:
        return jsonify({"error": f"No data found for {field_value} in from {start_time} to {end_time} time ."}), 404
    df = influx_handler.df_to_csv(df, iso_format=iso_format)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    # Seek to start
    buffer.seek(0)
    return Response(buffer.getvalue(), mimetype="text/csv",
                    headers={"Content-disposition": f'attachment; filename="{field_value}_{start_time}_to_{end_time}.csv"'})


@data_blueprint.route("/large-csv", methods=['GET', 'POST'])
def get_large_csv():
    """
    field_name - The name of the field to be queried.
    field_value - The value of the specified field to be queried.
    This will serve as the starting point for our query.
    If no end time is provided, this will also serve as our ending point for our query.
    If an end time is provided, then we will search from start_time until current time.

    :return: A csv file containing the queried data.
    :doc-author: Yukkei
    """
    endpoint = request.endpoint
    remote_ip = request.remote_addr
    print(f"Received a {request.method} request on endpoint {endpoint} from IP {remote_ip} at {datetime.now()}")
    if request.method == 'POST':
        print(f"Request json info {request.json}")
        field_name = request.json.get('field_name', "measurement")
        field_value = request.json.get('field_value')
        start_time = request.json.get('start_time')
        end_time = request.json.get('end_time', "-0s")
        iso_format_str = request.args.get('iso_format', 'False')

    elif request.method == 'GET':
        print(f"Request args info {request.args}")
        field_name = request.args.get('field_name', default="measurement")
        field_value = request.args.get('field_value')
        start_time = request.args.get('start_time', )
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time', "-0s")
        iso_format_str = request.args.get('iso_format', default='False')
    else:
        return jsonify({'message': 'Invalid request method'}), 400

    iso_format = iso_format_str.lower() == 'true'

    try:
        start_time = parse_time_input(start_time)
        end_time = parse_time_input(end_time) if end_time else datetime.utcnow()
        print(start_time, end_time)
    except ValueError:
        return jsonify({'message': 'time string should be ISO format in UTC time'}), 400

    def generate_data():
        interval = timedelta(minutes=5)
        current_time = start_time
        first_chunk = True
        print(f"Beginning to stream data from {start_time} to {end_time} to client.")

        while current_time < end_time:
            next_time = current_time + interval
            start_time_str = str(current_time.isoformat())
            end_time_str = str(next_time.isoformat())

            # Query your database for the current time interval
            df = influx_handler.query_as_dataframe(field_name=field_name, field_value=field_value,
                                                   start_time_str=start_time_str,
                                                   end_time_str=end_time_str)
            if df is None:
                current_time = next_time
                continue

            df = influx_handler.df_to_csv(df, iso_format=iso_format)
            # Check if DataFrame is not empty to avoid sending empty strings
            if not df.empty:
                # Convert DataFrame to CSV, omit header if it's not the first chunk
                yield df.to_csv(header=first_chunk, index=False)
                first_chunk = False
            print(f"Sent data from {start_time_str} to {end_time_str} to client.")
            current_time = next_time

    # Seek to start
    return Response(stream_with_context(generate_data()),
                    mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename="{field_value}_{start_time}_to_{end_time}.csv"'})
    # response = Response(generate_data(), mimetype='text/csv')
    # response.headers.set('Content-Disposition', 'attachment', filename=f'{field_value}_data.csv')
    # return response


@data_blueprint.route("/influx-query", methods=['GET'])
def execute_flux_query():
    """
    In danger of query injection. Not recommended to use in client side,
    keeping for testing or special use case.

    :return: The result of the query
    :doc-author: Yukkei
    """
    query = request.args.get('query')
    # current_app.logger.info(f"Received a POST request: {request.get_json()}")
    result = influx_handler.query_measurements(query)
    result = influx_handler.format_results(result)
    return jsonify(result), 200


@data_blueprint.route('/influx-stream', methods=['GET'])
def stream_from_influx():
    """
    A REST endpoint that allows the user to query the InfluxDB database for a specific field name and value.
    The function returns an event stream of data from the database, which can be
    used by a front-end api to display real-time data.

    :return: A stream of data from the database
    :doc-author: Yukkei
    """
    field_name = request.args.get('field_name')
    field_value = request.args.get('field_value')
    rate = request.args.get('rate', default=1)

    return Response(influx_handler.stream_data(field_name, field_value, rate=rate),
                    mimetype='text/event-stream')


@data_blueprint.route('/kafka-stream/latest/', methods=['GET'])
def get_latest_all():
    """
    Get the latest data for all sensors.
        ---
        tags:
          - Data Retrieval Functions

    :return: The latest data for all the sensors in the kafka stream
    :doc-author: Yukkei
    """
    kafka_latest_url = current_app.config["KAFKA_DISPATCHER_URL"] + "/latest"

    try:
        response = requests.get(kafka_latest_url, timeout=10)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Failed to retrieve data from the external service."}), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@data_blueprint.route('/kafka-stream/latest/<string:device_name>', methods=['GET'])
def get_latest(device_name):
    """
    The get_latest_data function returns the latest data for a given device.
        Args:
            device_name (str): The name of the device to get data from.

    :param device_name: Get the latest data for a specific device
    :return: The latest data for a device
    :doc-author: Yukkei
    """
    kafka_single_url = current_app.config["KAFKA_DISPATCHER_URL"] + "/latest/" + device_name

    try:

        response = requests.get(kafka_single_url, timeout=10)  # Adding a timeout for good practice

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Failed to retrieve data from the external service."}), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@data_blueprint.route('/kafka-stream/<device_name>', methods=['GET'])
def stream_from_kafka(device_name):
    """
    Streams the latest data from Kafka.
    """
    kafka_stream_url = current_app.config.get("KAFKA_DISPATCHER_URL", "") + "/" + device_name
    rate = request.args.get("rate", None)
    if rate:
        kafka_stream_url += f"?frequency={rate}"

    def generate():
        try:
            with requests.get(kafka_stream_url, stream=True) as r:
                # Check if the request was successful
                if r.status_code == 200:
                    # Stream the response content, chunk by chunk
                    for chunk in r.iter_content(chunk_size=4096):
                        yield chunk
                else:
                    # Handle error, maybe log it or yield an error message
                    yield f"Error: Failed to retrieve data, status code {r.status_code}\n".encode('utf-8')
        except Exception as e:
            current_app.logger.error(f"Failed to stream from Kafka for device {device_name}: {str(e)}")
            yield f"Error: Failed to connect to Kafka dispatcher service\n".encode('utf-8')

    # The Response should be created outside the generate function
    return Response(stream_with_context(generate()), content_type='text/event-stream')