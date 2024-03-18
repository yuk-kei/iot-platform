import io
import logging

from flask import Blueprint, request, jsonify, Response, current_app

from .kafka_handler import KafkaService, KafkaStreamHandler

kafka_blueprint = Blueprint('data', __name__, url_prefix="/api/v1/kafka-stream/")

kafka_service = KafkaService()
# kafka_service.subscribe(['sensor_data'])
kafka_handler = KafkaStreamHandler()
kafka_handler.start()


@kafka_blueprint.route('/test')
def test_connection():
    """
    Test the connection to the data blueprint

    :return: A string
    :doc-author: Yukkei
    """
    return '<h1>Connection Success</h1>'


@kafka_blueprint.route('/latest', methods=['GET'])
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


@kafka_blueprint.route('/<device_name>', methods=['GET'])
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
    endpoint = request.endpoint
    remote_ip = request.remote_addr
    print(f"Received a POST request on endpoint {endpoint} from IP {remote_ip}")
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




@kafka_blueprint.route('/latest/<string:device_name>', methods=['GET'])
def get_latest_data(device_name):
    """
    The get_latest_data function returns the latest data for a given device.
        Args:
            device_name (str): The name of the device to get data from.

    :param device_name: Get the latest data for a specific device
    :return: The latest data for a device
    :doc-author: Yukkei
    """
    current_app.logger.setLevel(logging.CRITICAL)
    global kafka_service
    global kafka_handler

    if not kafka_handler.running:
        return {'status': 'No stream running'}

    if device_name in kafka_handler.data and device_name in kafka_handler.flag:
        message = kafka_handler.get_latest_data_for_single(str(device_name))
        current_app.logger.setLevel(logging.WARNING)
        return message, 200
    current_app.logger.setLevel(logging.WARNING)
    return {'status': 'Device not ready'}, 404


@kafka_blueprint.route('/stop', methods=['GET'])
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


@kafka_blueprint.route('/kafka-stream/status', methods=['GET'])
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

@kafka_blueprint.route('/start', methods=['GET'])
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
