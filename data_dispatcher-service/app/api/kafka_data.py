import io
from datetime import datetime, timedelta

import requests
from flask import Blueprint, request, jsonify, Response, abort, current_app, stream_with_context
from apifairy import body, response, other_responses, arguments


kafka_blueprint = Blueprint('kafka-data', __name__, url_prefix="/api/v1/data/kafka")


@kafka_blueprint.route('/latest/', methods=['GET'])
@other_responses({200: 'All latest data.',
                  500: 'Kafka dispatcher service issue'})
def get_latest_all():
    """
    Get all the latest data from Kafka.

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


@kafka_blueprint.route('/latest/<string:device_name>', methods=['GET'])
@other_responses({200: 'All latest data.',
                  500: 'Kafka dispatcher service issue'})
def get_latest(device_name):
    """
    Get the Latest data for a single device

    - device_name: Get the latest data for a specific device

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


@kafka_blueprint.route('/<device_name>', methods=['GET'])
@other_responses({200: 'All latest data.',
                  500: 'Kafka dispatcher service issue'})
def stream_from_kafka(device_name):
    """
    Stream for a single device.
    It only streams when the sensor is keep emitting data now.
    It has another parameter "rate" to set the stream rate; default is 0 \n
    DO NOT DIRECT USE IN THE DOC UI!!

    - device_name: The name of the device to subscribe to.
    - rate: Optional frequency parameter to control the data sampling rate.
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
