import os
import gevent
import pytz
import pandas as pd

from influxdb_client.client import influxdb_client

from dateutil.parser import parse

"""
This module provides a class to handle data from InfluxDB.

Todo:
    * Implement the features of returning a result as csv file 
    * Implement the features of returning data as pandas dataframe
    * Implement other kinds of queries 

"""


class InfluxDataHandler:
    """
    A class to handle data from InfluxDB.
    """

    def __init__(self, client=None, bucket=None):
        """The __init__ function is called when the class is instantiated.
        It sets up the InfluxDB client and write/query APIs, as well as setting
        the bucket name to be used for writing data.

        :param self: Represent the instance of the class
        :param client: Connect to the influxdb server
        :param bucket: Specify the name of the bucket to retrieve data from
        :return: Self, which is the instance of the class
        :doc-author: Yukkei
        """
        self.client = influxdb_client.InfluxDBClient(
            url=os.environ.get('INFLUX_URL'),
            token=os.environ.get('INFLUX_TOKEN'),
            org=os.environ.get('INFLUX_ORG')
        ) if client is None else client

        self.write_api = self.client.write_api()
        self.query_api = self.client.query_api()
        self.bucket_name = os.environ.get('INFLUX_BUCKET') if bucket is None else bucket
        self.time_zone = pytz.timezone('America/Los_Angeles')

    def query_builder(self, query_dicts_list: list, start_time, end_time="0h", bucket_name=None):

        """ The query_builder function takes in a list of dictionaries, each containing the field name and value to be filtered on.
        It then builds a query string that can be used with the InfluxDBClient's query function.

        :param self: Make the function a method of the class
        :param query_dicts_list: list: Specify the fields and values that you want to filter by
        :param start_time: Specify the start time of the query
        :param end_time: Specify the end time of the query
        :param bucket_name: Specify the bucket to query
        :return: The query result
        :doc-author: Yukkei
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        query = f'from(bucket: "{bucket_name}") '
        query += f'|> range(start: {start_time}, stop:{end_time})'
        for query_dict in query_dicts_list:
            field_name = query_dict.get("field_name")
            field_value = query_dict.get("field_value")
            query += f'|> filter(fn: (r) => r["{field_name}"] == "{field_value}")'

        return query

    def search_data_influxdb(self, field_name, field_value, start_time_str, end_time_str="0h", frequency=None,
                             is_latest=None):
        """The search_data_influxdb function searches the InfluxDB database for a specific field value.

        :param is_latest:
        :param self: Bind the method to an object
        :param field_name: Specify the field that is being searched for
        :param field_value: Filter the data
        :param start_time_str: Specify the start time of the query
        :param end_time_str: Specify the end time of the query
        :param frequency: Aggregate the data
        :return: A list of dictionaries
        :doc-author: Yukkei
        """
        start_time = time_or_time_delta(start_time_str)
        end_time = time_or_time_delta(end_time_str)

        if field_name == "field" or field_name == "measurement" or field_name == "value":
            field_name = "_" + field_name

        query = f'from(bucket: "{self.bucket_name}") ' \
                f'|> range(start: {start_time}, stop:{end_time})' \
                f'|> filter(fn: (r) => r["{field_name}"] == "{field_value}")'

        if frequency is not None:
            frequency = time_or_time_delta(frequency)
            query += f'|> window(every: {frequency})' \
                     f'|> last()'
        if not frequency and is_latest:
            query += f'|> last()'

        result = self.query_api.query(query)

        return result

    def query_large_data(self, field_name, field_value, start_time, end_time="0h"):

        """ The query_large_data function is used to query large data sets from the InfluxDB database.
        The function takes in four arguments: field_name, field_value, start_time and end_time.
        The first two arguments are used to filter the results of the query by a specific value
        for a given field name (e.g., field_name == "field" or field_name == "measurement";).
        The last two arguments are used to specify a time range for which we want our data returned from (e.g., '-2h' or '2020-07-01T00:00:00Z').

        :param self: Represent the instance of the class
        :param field_name: Specify which field in the database we want to query
        :param field_value: Filter the data
        :param start_time: Specify the start time for the query
        :param end_time: Specify the end time of the query
        :return: A generator to stream data
        :doc-author: Yukkei
        """
        if field_name == "field" or field_name == "measurement" or field_name == "value":
            field_name = "_" + field_name

        query = f'from(bucket: "{self.bucket_name}") ' \
                f'|> range(start: {start_time}, stop:{end_time})' \
                f'|> filter(fn: (r) => r["{field_name}"] == "{field_value}")'

        large_stream = self.query_api.query_stream(query)

        for record in large_stream:
            local_time = record["_time"].astimezone()
            result_dict = {
                "time": local_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
                # "measurement": records["_measurement"],
                "field": record["_field"],
                "value": record["_value"]
            }

            yield f'data:{result_dict}\n\n'

        large_stream.close()

    def stream_data(self, field_name, field_value, rate=3, time_interval=3):

        """
        The stream_data function is a generator that continuously streams data from the InfluxDB database.
            The function takes in three arguments: field_name, field_value, and rate.
            The field name and value are used to query the database for specific data points.
            Rate is how often you want to stream new data from the database (in seconds).

        :param self: Represent the instance of the class
        :param field_name: Specify the field that we want to search for
        :param field_value: Specify the value of the field_name parameter
        :param rate: Control the speed of the stream
        :param time_interval: Set the time interval for which data is fetched from influxdb
        :return: A generator to stream data
        :doc-author: Yukkei
        """
        time_interval = f"-{time_interval}s"
        while True:
            # continuously stream data
            data = self.search_data_influxdb(field_name, field_value, time_interval)
            data = self.format_results(data)
            gevent.sleep(rate)

            yield f'data:{data}\n\n'

    def query_measurements(self, query):
        """
        Use to execute single query to influxdb, it is not recommended to direct use this function.
        :param query: Pass the query to the function
        :return: The result of the query
        :doc-author: Yukkei
        """

        return self.query_api.query(query)

    def format_results(self, result, frequency=None, use_local_time=False, iso_format=False):
        """
        The to_dict function takes the result of a query and converts it into a list of dictionaries.
        Each dictionary contains the time, measurement, field and value for each record in the result.

        :param use_local_time:
        :param frequency:
        :param result: Pass the result of the query to the function
        :return: A list of dictionaries
        :doc-author: Yukkei
        """
        result_dict = {}

        if frequency is not None and frequency > 0:
            # total_records = len(result[0].records)
            # sampling_point = int(total_records / frequency) + 1 if frequency is not None else None

            for table in result:
                for i, records in enumerate(table.records):

                    if i % frequency == 0:

                        time = records.get_time().astimezone(self.time_zone) if use_local_time else records.get_time()
                        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S.%f") if not iso_format else time.isoformat()

                        if formatted_time not in result_dict:
                            result_dict[formatted_time] = {}
                        result_dict[formatted_time][records["_field"]] = records.get_value()
        else:
            for table in result:
                for records in table.records:

                    time = records.get_time().astimezone(self.time_zone) if use_local_time else records.get_time()

                    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S.%f") if not iso_format else time.isoformat()

                    if formatted_time not in result_dict:
                        result_dict[formatted_time] = {}
                    result_dict[formatted_time][records["_field"]] = records.get_value()

        return result_dict

    def to_csv(self, results):

        rows = self.format_results(results)

        transformed_data = []
        for time, values in rows.items():
            row = {'time': time}
            row.update(values)
            transformed_data.append(row)

        # Create a DataFrame
        df = pd.DataFrame(transformed_data)

        return df


def time_or_time_delta(curr_time_str):
    """
    The time_or_time_delta function takes in a string and returns either the time delta or the time.
        If it is a timedelta, then it will return that value.
        If it is not, then we assume that this is an absolute timestamp and convert to seconds since epoch.

    :param curr_time_str: Pass in the current time string
    :return: A datetime object
    :doc-author: Yukkei
    """
    if len(curr_time_str) == 1:
        return "Invalid time format"
    if curr_time_str[-1] == 'd':
        return curr_time_str
    elif curr_time_str[-1] == 'h':
        return curr_time_str
    elif curr_time_str[-1] == 'm':
        return curr_time_str
    elif curr_time_str[-1] == 's':
        return curr_time_str

    try:
        target_time = parse(curr_time_str)

        target_time_seconds = int(target_time.timestamp())
        return target_time_seconds

    except ValueError:
        print(f"Error: unable to parse time string {curr_time_str}")
