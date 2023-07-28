import os
from datetime import datetime, timedelta

from influxdb_client.client import influxdb_client

client = influxdb_client.InfluxDBClient(
    url=os.environ.get('INFLUX_URL'),
    token=os.environ.get('INFLUX_TOKEN'),
    org="calit2"
)

write_api = client.write_api()
query_api = client.query_api()
bucket_name = "sensor_data"

# Calculate time range for the query
now = datetime.utcnow()
one_hour_ago = now - timedelta(hours=1)


def test():
    record = search_data_influxdb("measurement", "Device 1", "-1h")
    output = record.to_json(indent=2)
    print(output)


def search_data_influxdb(field_name, field_value, start_time, end_time="0h"):
    query = f'from(bucket: "{bucket_name}") ' \
            f'|> range(start: {start_time}, stop:{end_time})'\
            f'|> filter(fn: (r) => r["_{field_name}"] == "{field_value}")'
    result = query_api.query(query)
    return result


def query_measurements(query):
    result = query_api.query(query)
    return result


if __name__ == '__main__':
    test()
    # app.run()
