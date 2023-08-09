import time

import socketio
import requests

sio = socketio.Client()

sensor_id = "1690575489c119600f"  # replace with your sensor ID

@sio.on('connect', namespace='/kafka')
def on_connect():
    print("I'm connected to the namespace!")


@sio.on('data_stream', namespace='/kafka')
def on_data_stream(data):
    print("New data received: ", data)

@sio.on('disconnect')
def on_disconnect():
    print("I'm disconnected!")


sio.connect('http://127.0.0.1:5000', namespaces=['/kafka'])

#     # sio.emit('join', {'sensor_id': sensor_id})
#

# @sio.event
# def connect():
#     print("I'm connected!")
#     sio.emit('join', {'sensor_id': sensor_id})
#
#
#
# @sio.event
# def disconnect():
#     print("I'm disconnected!")
#     # sio.emit('join', {'sensor_id': sensor_id})


# @sio.event
# def sensor_data(data):
#     # sio.emit('join', {'sensor_id': sensor_id})
#     print("New data received: ", data)


# response = requests.get('http://localhost:5000/start_stream/' + sensor_id)
# print(response.json())
# sio.connect('http://127.0.0.1:5000', wait_timeout=10)

try:
    sio.wait()  # Keep the client running to receive events
except KeyboardInterrupt:
    print("Disconnecting from the server...")
    sio.disconnect()
