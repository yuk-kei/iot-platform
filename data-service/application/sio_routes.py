import logging

from flask_socketio import SocketIO, Namespace, emit
from flask import request, Blueprint, Flask

from .kafka_handler import KafkaService, KafkaSocketIO

logger = logging.getLogger(__name__)

kafka_blueprint = Blueprint('kafka', __name__, url_prefix="/api/kafka")

socketio = SocketIO(async='gevent',cors_allowed_origins='*')

kafka_service = None
kafka_background = None


@kafka_blueprint.route('/test/')
def test_connection():
    return '<h1>Connection Success</h1>'


@kafka_blueprint.route('/start_stream/')
def start_stream_endpoint():
    global kafka_service
    global kafka_background
    global socketio
    if kafka_service is None:
        kafka_service = KafkaService()
        kafka_service.subscribe(['sensor_data'])

    if kafka_background is None:
        kafka_background = KafkaSocketIO(socketio, kafka_service, 'data_stream', '/kafka')
        print("starting a thread")
        kafka_background.start()
        print("not a background thread")
        return {'status': 'Stream started'}
    else:
        return {'status': 'Stream already running'}


@kafka_blueprint.route('/stop_stream/')
def stop_stream():
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
            logger.error(f"Error stopping stream: {str(e)}")
            return {'status': 'Error stopping stream', 'error': str(e)}

    else:
        return {'status': 'No stream to stop'}


@kafka_blueprint.route('/pause_stream/')
def pause_stream():
    global kafka_background
    # print(kafka_background.states)
    if kafka_background is not None and kafka_background.state == 'running':
        kafka_background.pause()
        return {'status': 'Stream paused'}
    else:
        return {'status': 'No stream to pause'}


@kafka_blueprint.route('/resume_stream/')
def resume_stream():
    global kafka_background

    if kafka_background is not None and kafka_background.state == 'pause':
        kafka_background.resume()
        return {'status': 'Stream resumed'}
    else:
        return {'status': 'No stream to resume'}


class KafkaStreamNamespace(Namespace):
    def on_connect(self):
        print('Client connected', request.sid)

    def on_disconnect(self):
        print('Client disconnected', request.sid)


socketio.on_namespace(KafkaStreamNamespace('/kafka'))

# if __name__ == '__main__':
#     app = Flask(__name__)
#     app.register_blueprint(kafka_blueprint)
#     socketio.init_app(app)
#     socketio.run(app, port=5000)
