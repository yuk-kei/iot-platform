import os

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

    def search_data_influxdb(self, field_name, field_value, start_time, end_time="0h"):
        query = f'from(bucket: "{self.bucket_name}") ' \
                f'|> range(start: {start_time}, stop:{end_time})' \
                f'|> filter(fn: (r) => r["_{field_name}"] == "{field_value}")'
        result = self.query_api.query(query)
        return result

    def query_large_data(self, field_name, field_value, start_time, end_time="0h"):
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
                    "measurement": records["_measurement"],
                    "field": records["_field"],
                    "value": records["_value"]
                })
        return list_of_dict


"""test code"""
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
