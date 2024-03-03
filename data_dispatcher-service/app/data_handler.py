import os
import time

import pytz
import pandas as pd

from influxdb_client.client import influxdb_client
from .utils import time_or_time_delta


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
            org=os.environ.get('INFLUX_ORG'),
            timeout= 180 * 1000
        ) if client is None else client

        self.write_api = self.client.write_api()
        self.query_api = self.client.query_api()
        self.bucket_name = os.environ.get('INFLUX_BUCKET') if bucket is None else bucket
        self.time_zone = pytz.timezone('America/Los_Angeles')

    def query_as_dataframe(self, field_name, field_value, start_time_str, end_time_str="0h", frequency=None,
                           is_latest=None):
        """The search_data_influxdb function searches the InfluxDB database for a specific field value.

        :param field_name: Specify the field that is being searched for
        :param field_value: Filter the data
        :param start_time_str: Specify the start time of the query
        :param end_time_str: Specify the end time of the query
        :return: dataframe
        :doc-author: Yukkei
        """
        start_time = time_or_time_delta(start_time_str)
        end_time = time_or_time_delta(end_time_str)

        if field_name == "field" or field_name == "measurement" or field_name == "value":
            field_name = "_" + field_name

        query = f'import "experimental"' \
                f'from(bucket: "{self.bucket_name}") ' \
                f'|> range(start: {start_time}, stop:{end_time})' \
                f'|> filter(fn: (r) => r["{field_name}"] == "{field_value}")'

        if frequency is not None:
            frequency = time_or_time_delta(frequency)
            query += f'|> window(every: {frequency})' \
                     f'|> last()'
        if not frequency and is_latest:
            query += f'|> last()'

        query += f'|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")' \
                 f'|> drop(columns:["_start", "_stop", "host", "id", "output", "_measurement"])'

        result = self.query_api.query_data_frame(query)
        if result.empty:
            return
        result.drop(columns=["result", "table"], inplace=True)

        result['_time'] = pd.to_datetime(result['_time'])

        result.rename(columns={'_time': 'time'}, inplace=True)
        return result

    def df_to_csv(self, results_df, iso_format=False):
        # Convert '_time' from UTC to Los Angeles time
        if results_df['time'].dt.tz is None:
            results_df['time'] = results_df['time'].dt.tz_localize('UTC')  # Assuming the times are in UTC; adjust if necessary
        results_df['local_time'] = results_df['time'].dt.tz_convert(self.time_zone)
        column_order = ['time', 'local_time'] + [col for col in results_df.columns if
                                                 col not in ['time', 'local_time']]
        results_df = results_df.reindex(columns=column_order)
        if not iso_format:
            results_df['time'] = results_df['time'].dt.strftime("%Y-%m-%d %H:%M:%S.%f")
            results_df['local_time'] = results_df['local_time'].dt.strftime("%Y-%m-%d %H:%M:%S.%f") \
                if 'local_time' in results_df.columns else None

        return results_df

    def df_to_dict(self, results_df):
        results_df['time'] = results_df['time'].dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        results_df.set_index('time', inplace=True)
        return results_df.to_dict(orient='index')

    def stream_data(self, field_name, field_value, rate=1):

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
        time_interval = f"-{rate + 5}s"
        while True:
            # continuously stream data
            data = self.query_as_dataframe(field_name, field_value, start_time_str=time_interval, is_latest=True)

            if data is None:
                time.sleep(int(rate))
                continue

            data = self.df_to_dict(data)
            yield f'data:{data}\n\n'
            time.sleep(int(rate))

    def query_measurements(self, query):
        """
        Use to execute single query to influxdb, it is not recommended to direct use this function.
        :param query: Pass the query to the function
        :return: The result of the query
        :doc-author: Yukkei
        """

        return self.query_api.query(query)

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
                        time = records.get_time()
                        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S.%f") if not iso_format else time.isoformat()

                        if formatted_time not in result_dict:
                            result_dict[formatted_time] = {}

                        if use_local_time:
                            local_time = time.astimezone(self.time_zone) if use_local_time else records.get_time()
                            formatted_local_time = local_time.strftime(
                                "%Y-%m-%d %H:%M:%S.%f") if not iso_format else local_time.isoformat()
                            result_dict[formatted_time]["local_time"] = formatted_local_time

                        result_dict[formatted_time][records["_field"]] = records.get_value()
        else:
            for table in result:
                for records in table.records:

                    time = records.get_time()
                    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S.%f") if not iso_format else time.isoformat()

                    if formatted_time not in result_dict:
                        result_dict[formatted_time] = {}
                    if use_local_time:
                        local_time = time.astimezone(self.time_zone)
                        formatted_local_time = local_time.strftime(
                            "%Y-%m-%d %H:%M:%S.%f") if not iso_format else local_time.isoformat()
                        result_dict[formatted_time]["local_time"] = formatted_local_time

                    result_dict[formatted_time][records["_field"]] = records.get_value()

        return result_dict

    def to_csv(self, formatted_results):

        rows = formatted_results

        transformed_data = []
        for time, values in rows.items():
            row = {'time': time}
            row.update(values)
            transformed_data.append(row)

        # Create a DataFrame
        df = pd.DataFrame(transformed_data)

        return df



