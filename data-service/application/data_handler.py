import os
import gevent

from influxdb_client.client import influxdb_client

from dateutil.parser import parse


class InfluxDataHandler:
    def __init__(self, client=None, bucket=None):

        self.client = influxdb_client.InfluxDBClient(
            url=os.environ.get('INFLUX_URL'),
            token=os.environ.get('INFLUX_TOKEN'),
            org=os.environ.get('INFLUX_ORG')
        ) if client is None else client

        self.write_api = self.client.write_api()
        self.query_api = self.client.query_api()
        self.bucket_name = os.environ.get('INFLUX_BUCKET') if bucket is None else bucket

    def query_builder(self, query_dicts_list: list, start_time, end_time="0h", bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket_name

        query = f'from(bucket: "{bucket_name}") '
        query += f'|> range(start: {start_time}, stop:{end_time})'
        for query_dict in query_dicts_list:
            field_name = query_dict.get("field_name")
            field_value = query_dict.get("field_value")
            query += f'|> filter(fn: (r) => r["{field_name}"] == "{field_value}")'

        return query

    def search_data_influxdb(self, field_name, field_value, start_time_str, end_time_str="0h", frequency=None):
        start_time = time_or_time_delta(start_time_str)

        end_time = time_or_time_delta(end_time_str)

        if field_name == "field" or field_name == "measurement" or field_name == "value":
            field_name = "_" + field_name

        query = f'from(bucket: "{self.bucket_name}") ' \
                f'|> range(start: {start_time}, stop:{end_time})' \
                f'|> filter(fn: (r) => r["{field_name}"] == "{field_value}")'
        if frequency is not None:
            frequency = time_or_time_delta(frequency)
            query += f'|> aggregateWindow(every: {frequency}, fn: mean, createEmpty: false)'
            query += f'|> yield(name: "mean")'  # Not sure if this is needed
            # query += f'|> map(fn: (r) => ({{r with _time: r._time + {frequency}}}))'
        result = self.query_api.query(query)
        return result

    def query_large_data(self, field_name, field_value, start_time, end_time="0h"):
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

    def stream_data(self, field_name, field_value, rate=1, auto_refresh=2):
        auto_refresh_str = f"-{auto_refresh}s"
        while True:  # continuously stream data
            data = self.search_data_influxdb(field_name, field_value, auto_refresh_str)
            data = self.to_dict(data)
            gevent.sleep(rate)
            print(data)
            yield f'data:{data}\n\n'
            # for item in data:
            #     yield item

    def query_measurements(self, query):

        return self.query_api.query(query)

    def to_dict(self, result):

        list_of_dict = []
        for table in result:
            for records in table.records:
                local_time = records["_time"].astimezone()
                list_of_dict.append({
                    "time": local_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    # "measurement": records["_measurement"],
                    "field": records["_field"],
                    "value": records["_value"]
                })
        return list_of_dict


def time_or_time_delta(curr_time_str):
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


"""test code"""
