import json
import os
import gevent
from datetime import timedelta


from flask import jsonify

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

    def search_data_influxdb(self, field_name, field_value, start_time_str, end_time_str="0h"):
        start_time = time_or_time_delta(start_time_str)

        end_time = time_or_time_delta(end_time_str)

        if field_name == "field" or field_name == "measurement" or field_name == "value":
            field_name = "_" + field_name

        query = f'from(bucket: "{self.bucket_name}") ' \
                f'|> range(start: {start_time}, stop:{end_time})' \
                f'|> filter(fn: (r) => r["{field_name}"] == "{field_value}")'
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
                "time": local_time.strftime("%Y-%m-%d %H:%M:%S"),
                # "measurement": records["_measurement"],
                "field": record["_field"],
                "value": record["_value"]
            }

            yield json.dumps(result_dict)

        large_stream.close()

    def stream_data(self, field_name, field_value, auto_refresh):
        auto_refresh_str = f"-{auto_refresh}s"
        while True:  # continuously stream data
            data = self.search_data_influxdb(field_name, field_value, auto_refresh_str)
            data = self.to_dict(data)
            yield f'data:{data}\n\n'.encode()
            # for item in data:
            #     yield item
            gevent.sleep(auto_refresh - 1)

    def query_measurements(self, query):

        return self.query_api.query(query)

    def to_dict(self, result):

        list_of_dict = []
        for table in result:
            for records in table.records:
                local_time = records["_time"].astimezone()
                list_of_dict.append({
                    "time": local_time.strftime("%Y-%m-%d %H:%M:%S"),
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

# client = influxdb_client.InfluxDBClient(
#     url="http://128.195.151.182:8086",
#     token="FzxLoZXd06eIEYzueFsX1Kj21w5LwClTr4TC0w6NrWhzuBqeAVl0Sb9Nqiut5HRNZqcHgIzd0CalUl1__AynLw==",
#     org="calit2")
# write_api = client.write_api()
# query_api = client.query_api()
# bucket_name = "sensor_data"
# data_handler = InfluxDataHandler(client, bucket_name)
#
#
# data_sink = Stream()
# data_example = pd.DataFrame({'_value': []}, columns=['_value'])
# data_df = DataFrame(data_sink, example=data_example)
# field_name = "id"
# field_value = "1690575489c119600f"
#
# flux_query = f'''from(bucket: "{bucket_name}")
#             |> range(start: -10d)
#             |> filter(fn: (r) => r["_{field_name}"] == "{field_value}")
#             '''
# for record in data_handler.query_large_data(field_name, field_value, start_time="-10d"):
#     print(record)

# data_handler.source_data_to_socket(auto_refresh=5, query=query, sink=data_sink)
# data_df.hvplot.line(x='time', y='values', line_width=2, color='red').opts(width=1000, height=400)
# data_handler.source_data(auto_refresh=5, query=query)

# input_time1 = "2023-08-01T18:00:00.000Z"
# input_time2 = "2023-08-01T18:39:00.000Z"
# output1 = time_or_time_delta(input_time1)
# output2 = time_or_time_delta(input_time2)
# print(output1)
# print(output2)
# client = influxdb_client.InfluxDBClient(
#     url="http://128.195.151.182:8086",
#     token="FzxLoZXd06eIEYzueFsX1Kj21w5LwClTr4TC0w6NrWhzuBqeAVl0Sb9Nqiut5HRNZqcHgIzd0CalUl1__AynLw==",
#     org="calit2"
# )
# query_api = client.query_api()
# tables = query_api.query(f'from(bucket:"sensor_data") |> range(start: {output1}, stop:{output2}) '
#                                     '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '
#                                     '|> keep(columns: ["time", "values"])')
# print(tables)
# df = query_api.query_data_frame(f'from(bucket:"sensor_data") |> range(start: -21h) '
#                                 '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '
#                                 '|> keep(columns: ["time", "values"])')
# query = f'from(bucket:"sensor_data") |> range(start: {output1}, stop:{output2})'
# result = query_api.query(query)
# print(result)
# for table in result:
#
#     for record in table.records:
#
#         print(str(record["_time"]) + " - " + record["_field"] + ": " + str(record["_value"]))
