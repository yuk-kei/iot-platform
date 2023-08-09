import json
import threading


from flask import Flask, Blueprint
from flask_socketio import SocketIO, join_room
from application.kafka_handler import KafkaService

test = Blueprint('test', __name__)

socketio = SocketIO(async_mode=None)
sensor_streams = {}


def start_stream(sensor_id, socketio):
    kafka_service = KafkaService({
        'bootstrap.servers': '128.195.151.182:9392',
        'group.id': 'data-dispatcher',
        'auto.offset.reset': 'latest'
    })
    kafka_service.subscribe(['sensor_data'])
    # replace with your Kafka topic
    for msg in kafka_service.gen_messages():
        msg_json = json.loads(msg)
        if msg_json['id'] == sensor_id:  # or use msg_json['id'] == sensor_id if you want to filter by id
            print(msg_json)
            socketio.emit('sensor_data', msg_json, room=sensor_id)


@test.route('/start_stream/<sensor_id>')
def start_stream_endpoint(sensor_id):
    if sensor_id not in sensor_streams or not sensor_streams[sensor_id].is_alive():
        sensor_streams[sensor_id] = threading.Thread(target=start_stream, args=(sensor_id, socketio))
        sensor_streams[sensor_id].start()
        return {'status': 'Stream started'}
    else:
        return {'status': 'Stream already running'}


@socketio.on('join')
def on_join(data):
    sensor_id = data['sensor_id']
    join_room(sensor_id)


@test.route('/stop_stream/<sensor_id>')
def stop_stream(sensor_id):
    global sensor_streams
    if sensor_id in sensor_streams:
        sensor_streams[sensor_id].do_run = False
        sensor_streams[sensor_id].join()
        del sensor_streams[sensor_id]
        return {'status': 'Stream stopped'}
    else:
        return {'status': 'No stream to stop'}


def create_app():
    app = Flask(__name__)
    app.register_blueprint(test)

    socketio.init_app(app)
    return socketio, app


# if __name__ == "__main__":
#     # app.register_blueprint(test)
#     socketio, app = create_app()
#     socketio.run(app)
#     # app.run()
