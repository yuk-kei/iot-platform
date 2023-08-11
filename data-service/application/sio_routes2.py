from threading import Lock
from flask_socketio import SocketIO, Namespace, emit
from flask import request, Blueprint, Flask

from .kafka_handler import KafkaService, KafkaSocketIO

kafka_blueprint = Blueprint('kafka', __name__, url_prefix="/api/kafka")

socketio = SocketIO(cors_allowed_origins='*', async_mode=None, logger=True, engineio_logger=True)

kafka_thread = None
thread_lock = Lock()


def background_thread():
    kafka_service = KafkaService({
        'bootstrap.servers': '128.195.151.182:9392',
        'group.id': 'data-dispatcher',
        'auto.offset.reset': 'latest'
    })
    kafka_service.subscribe(['sensor_data'])
    while True:

        msg = kafka_service.receive()
        if msg is not None:
            print(msg)
            socketio.emit('data_stream', msg)


@socketio.event
def connect():
    global kafka_thread
    with thread_lock:
        if kafka_thread is None:
            kafka_thread = socketio.start_background_task(background_thread)
    emit('connect', 'Connected')


@socketio.event
def disconnect():
    print('Client disconnected', request.sid, )


@kafka_blueprint.route('/test/')
def test_connection():
    return '<h1>Connection Success</h1>'


@kafka_blueprint.route('/start_stream/')
def start_stream_endpoint():
    pass


@kafka_blueprint.route('/stop_stream/')
def stop_stream():
    pass


@kafka_blueprint.route('/pause_stream/')
def pause_stream():
    pass


@kafka_blueprint.route('/resume_stream/')
def resume_stream():
    pass


# if __name__ == '__main__':
#     app = Flask(__name__)
#     app.register_blueprint(kafka_blueprint)
#     socketio.init_app(app)
#     socketio.run(app, port=5000)
