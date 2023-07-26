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
        result = self.query_api.query(query)
        return result


