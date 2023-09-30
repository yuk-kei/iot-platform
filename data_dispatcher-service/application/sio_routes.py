import os

from flask_socketio import SocketIO, Namespace
from flask import request, Blueprint

from .kafka_handler import KafkaService, KafkaSocketIO
"""
    This file is used to create the Kafka socketio endpoints
    It creates a KafkaService object and a KafkaSocketIO object
    The KafkaSocketIO object is a thread that handles the connection to Kafka
    and emits events to the client
    The KafkaService object is used to subscribe to topics and receive data from Kafka
    
    Todo:
        * Emit the arrived data to the seperate rooms (for each sensor)
        * Use a message queue to support multiple processes (for scaling) 
"""

kafka_blueprint = Blueprint('kafka', __name__, url_prefix="/api/kafka")
socketio = SocketIO(cors_allowed_origins='*')
kafka_service = None
kafka_background = None


@kafka_blueprint.route('/test/')
def test_connection():
    """
    test the connection

    :return: the connection status
    :doc-author: Yukkei
    """

    return '<h1>Connection Success</h1>'


@kafka_blueprint.route('/start_stream/')
def start_stream_endpoint():
    """
    The start_stream_endpoint function starts a background thread that listens to the Kafka topic 'sensor_data' and emits
    the data it receives from this topic to the client via SocketIO.
    The function returns a status message indicating whether the stream was started.

    :return: A dictionary with a key status and the value stream started
    :doc-author: Yukkei
    """
    global kafka_service
    global kafka_background
    global socketio

    if kafka_service is None:
        kafka_service = KafkaService({
            'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS'),
            'group.id': os.environ.get('KAFKA_SIO_GROUP_ID'),
            'auto.offset.reset': os.environ.get('KAFKA_AUTO_OFFSET_RESET')
        })
        kafka_service.subscribe(['sensor_data'])

    if kafka_background is None:
        kafka_background = KafkaSocketIO(socketio, kafka_service, 'data_stream', '/kafka')
        print("starting a thread")
        kafka_background.start()

        return {'status': 'Stream started'}
    else:
        return {'status': 'Stream already running'}


@kafka_blueprint.route('/stop_stream/')
def stop_stream():
    """
    The stop_stream function stops the Kafka stream.
        Returns:
            A dictionary with a status message and an error message if applicable.


    :return: A dictionary with a status key
    :doc-author: Yukkei
    """
    global kafka_background
    global kafka_service

    if kafka_background is not None:
        try:
            kafka_background.stop()
            kafka_background.join(timeout=10)
            kafka_background = None
            kafka_service = None
            return {'status': 'Stream stopped'}
        except Exception as e:
            print(f"Error stopping stream: {str(e)}")
            return {'status': 'Error stopping stream', 'error': str(e)}

    else:
        return {'status': 'No stream to stop'}


@kafka_blueprint.route('/pause_stream/')
def pause_stream():
    """
    The pause_stream function pauses the stream of data from Kafka.
        :return: A JSON object with a status message indicating whether the stream was paused.


    :return: A dictionary with a status key
    :doc-author: Trelent
    """
    global kafka_background

    if kafka_background is not None and kafka_background.state == 'running':
        kafka_background.pause()
        return {'status': 'Stream paused'}
    else:
        return {'status': 'No stream to pause'}


@kafka_blueprint.route('/resume_stream/')
def resume_stream():
    """
    The resume_stream function resumes the stream if it is paused.
        Returns:
            A dictionary with a status message indicating whether the stream was resumed.

    :return: A dictionary with the status of the stream
    :doc-author: Trelent
    """
    global kafka_background

    if kafka_background is not None and kafka_background.state == 'pause':
        kafka_background.resume()
        return {'status': 'Stream resumed'}
    else:
        return {'status': 'No stream to resume'}


class KafkaStreamNamespace(Namespace):
    """
    This class is used to handle the socketio connection and events
    More features can be added here
    """
    def on_connect(self):
        print('Client connected', request.sid)

    def on_disconnect(self):
        print('Client disconnected', request.sid)


socketio.on_namespace(KafkaStreamNamespace('/kafka'))
