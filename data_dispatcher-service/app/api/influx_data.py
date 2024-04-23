import io
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, Response, abort
from apifairy import body, response, other_responses, arguments
from app.data_handler import InfluxDataHandler
from app.utils import parse_time_input
from app.schemas import (QueryRequestSchema, LatestQueryRequestSchema, CSVRequestSchema,
                       StreamCSVRequestSchema, DirectQuerySchema, QueryStreamSchema)

"""
    Data Blueprint
    This blueprint is responsible for handling data requests.
    The blueprint is registered in the app.py file.
    All api in this file are prefixed with /api/v1/influx

    The blueprint is responsible for handling all requests related to the data.
    This includes:
        - Querying data from the influxdb
        - Streaming large data from the influxdb

    The blueprint uses the data_handler.py file to interact with the influxdb.
    The blueprint uses the kafka_handler.py file to interact with the kafka.
"""

influx_blueprint = Blueprint('influx-data', __name__, url_prefix="/api/v1/data/influx")

influx_handler = InfluxDataHandler()


@influx_blueprint.route("/query", methods=['GET'])
@arguments(QueryRequestSchema)
@other_responses({200: 'Return the given range data form Influx DB.',
                  404: 'No data found for in this time range'})
def query_influx_data(query):
    """
    Query form db
    """
    device_name = query.get('device_name')
    start_time = query.get('start_time')
    end_time = query.get('end_time')
    frequency = query.get('frequency', None)

    field_name = "measurement"
    df = influx_handler.query_as_dataframe(field_name, device_name, start_time, end_time, frequency=frequency)
    if df is None:
        error_response = {"error": f"No data found for {device_name} in the {start_time} to {end_time} time range."}
        abort(404, description=error_response)

    result = influx_handler.df_to_dict(df)

    return jsonify(result)


@influx_blueprint.route("/query/latest", methods=['GET'])
@arguments(LatestQueryRequestSchema)
@other_responses({200: 'Return the latest data from InfluxDB in a custom time range.',
                  404: 'No data found for in this time range'})
def query_latest_data(query):
    """
    Get latest from db

    """
    field_name = "measurement"
    device_name = query.get('device_name')
    start_time = query.get('start_time')
    end_time = query.get('end_time')

    df = influx_handler.query_as_dataframe(field_name,
                                           device_name,
                                           start_time,
                                           end_time,
                                           frequency=None,
                                           is_latest=True)
    if df is None:
        error_response = {"error": f"No data found for {device_name} in the {start_time} to {end_time} time range."}
        abort(404, description=error_response)

    result = influx_handler.df_to_dict(df)

    return jsonify(result)


@influx_blueprint.route("/csv", methods=['GET'])
@arguments(CSVRequestSchema)
@other_responses({200: 'A CSV file will be downloaded containing the data.',
                  404: 'No data found for in this time range'})
def get_csv(query):
    """
    Get csv file

    This endpoint downloads the csv file in a certain time range for a device. It is suitable for a small amount of data

    """
    # endpoint = request.endpoint
    # remote_ip = request.remote_addr
    # print(f"Received a POST request on endpoint {endpoint} from IP {remote_ip}")
    field_name = "measurement"
    device_name = query.get('device_name')
    start_time = query.get('start_time')
    end_time = query.get('end_time')
    frequency = query.get('frequency', None)
    iso_format = query.get('iso_format', False)
    df = influx_handler.query_as_dataframe(field_name=field_name, field_value=device_name,
                                           start_time_str=start_time,
                                           frequency=frequency,
                                           end_time_str=end_time
                                           )

    if df is None or df.empty:  # Check if df is None or empty
        error_response = {"error": f"No data found for {device_name} in the {start_time} to {end_time} time range."}
        abort(404, description=error_response)
    df = influx_handler.df_to_csv(df, iso_format=iso_format)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)

    # Seek to start
    buffer.seek(0)
    return Response(buffer.getvalue(), mimetype="text/csv",
                    headers={"Content-disposition": f'"attachment; filename={device_name}_data.csv"'})


@influx_blueprint.route("/large-csv", methods=['GET'])
@arguments(StreamCSVRequestSchema)
@other_responses({200: 'A CSV file will be downloaded containing the data.',
                  400: 'Time format issue'})
def get_large_csv(query):
    """
    Stream csv file

    This endpoint downloads csv file from InfluxDB using Server-Sent Events (SSE).
    It is suitable for a large amount of data like more than 1 day
    \n
    DO NOT TRY IT DIRECTLY IN THE DOC UI!!! \n
    You can paste the url in the request sample on the right side to the browser once you fill out the parameters
    """
    field_name = "measurement"
    device_name = query.get('device_name')
    start_time = query.get('start_time')
    end_time = query.get('end_time')
    iso_format = query.get('iso_format', False)

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

        while current_time < end_time:
            next_time = current_time + interval
            start_time_str = str(current_time.isoformat())
            end_time_str = str(next_time.isoformat())

            # Query your database for the current time interval
            df = influx_handler.query_as_dataframe(field_name=field_name, field_value=device_name,
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

            current_time = next_time

    # Seek to start
    response = Response(generate_data(), mimetype='text/csv')
    response.headers.set('Content-Disposition', 'attachment', filename=f'{device_name}_data.csv')
    return response


@influx_blueprint.route("/influx-query", methods=['GET'])
@arguments(DirectQuerySchema)
def execute_flux_query(args):
    """
    Direct query db
    Waring!!!!In danger of query injection. Not recommended to use in client side
    """
    query = args['query']
    # current_app.logger.info(f"Received a POST request: {request.get_json()}")
    result = influx_handler.query_measurements(query)
    result = influx_handler.format_results(result)
    return jsonify(result), 200


@influx_blueprint.route('/influx-stream', methods=['GET'])
@arguments(QueryStreamSchema)
@other_responses({200: 'Streaming data from InfluxDB.', 400: 'Invalid parameters'})
def stream_from_influx(query):
    """
    Stream data from InfluxDB.

    This endpoint streams data from InfluxDB using Server-Sent Events (SSE). \n
    DO NOT TRY IT DIRECTLY IN THE DOC UI!!! \n
    You can paste the url in the request sample on the right side to the browser once you fill out the parameters

    Parameters:
    - field_name: The name of the field to stream.
    - field_value: The value of the field to match for streaming.
    - rate: The rate (in seconds) at which data is sampled and sent. Default is 1 second.
    """
    device_name = query.get('device_name')
    rate = query.get('rate')
    field_name = "measurement"
    return Response(influx_handler.stream_data(field_name, device_name, rate=rate),
                    mimetype='text/event-stream')