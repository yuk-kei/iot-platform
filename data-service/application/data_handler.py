import os
from datetime import datetime

from influxdb_client.client import influxdb_client


class InfluxDataHandler:
    def __init__(self):
        self.client = influxdb_client.InfluxDBClient(
            url=os.environ.get('INFLUX_URL'),
            token=os.environ.get('INFLUX_TOKEN'),
            org=os.environ.get('INFLUX_ORG')
        )

        self.write_api = self.client.write_api()
        self.query_api = self.client.query_api()
        self.bucket_name = os.environ.get('INFLUX_BUCKET')

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
                f'|> filter(fn: (r) => r["_{field_name}"] == "{field_value}")'
        large_stream = self.query_api.query_stream(query)
        large_stream.close()
        return large_stream

    def query_measurements(self, query):

        return self.query_api.query(query)

    def to_dict(self, result):

        list_of_dict = []
        for table in result:
            for records in table.records:
                list_of_dict.append({
                    "time": records["_time"],
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
        target_time = datetime.strptime(curr_time_str, '%Y-%m-%dT%H:%M:%S')
        # target_time += utc_offset
        target_time_seconds = int(target_time.timestamp())
        return target_time_seconds

    except ValueError:
        try:
            target_time = datetime.strptime(curr_time_str, '%Y-%m-%dT%H:%M')

            target_time_seconds = int(target_time.timestamp())
            return target_time_seconds
        except ValueError:
            print(f"Error: unable to parse time string {curr_time_str}")




"""test code"""
input_time1 = "2023-07-31T15:30"
output1 = time_or_time_delta(input_time1)
print(output1)
# client = influxdb_client.InfluxDBClient(
#     url="http://128.195.151.182:8086",
#     token="FzxLoZXd06eIEYzueFsX1Kj21w5LwClTr4TC0w6NrWhzuBqeAVl0Sb9Nqiut5HRNZqcHgIzd0CalUl1__AynLw==",
#     org="calit2"
# )
# query_api = client.query_api()
# tables = query_api.query_data_frame('from(bucket:"sensor_data") |> range(start: -20h)')
#
# df = query_api.query_data_frame('from(bucket:"sensor_data") |> range(start: -21h) '
#                                 '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '
#                                 '|> keep(columns: ["time", "values"])')
# print(tables.to_string())
# for table in tables:
#
#     for record in table.records:
#
#         print(str(record["_time"]) + " - " + record["_field"] + ": " + str(record["_value"]))
