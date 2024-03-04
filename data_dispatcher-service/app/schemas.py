from marshmallow import validate, fields, validates, validates_schema, \
    ValidationError, post_dump, pre_load

from app import ma

from marshmallow import Schema, fields


# Common request schema for GET and POST methods
class QueryRequestSchema(ma.Schema):
    device_name = fields.String(required=True, description='The device or service name')
    start_time = fields.String(required=True, description='Start time string, either with standard ISO time format '
                                                          'or relative time like "-10s", "-30m", "-24h", "-3d"')
    end_time = fields.String(missing="-0s", description='End time string, either with standard ISO time format '
                                                        'or relative time like "-20s", "-60m", "-48h", "-7d"')
    frequency = fields.String(missing=None, description='frequency, sample usage as "10s", "10m", "1h", "1d"')


class LatestQueryRequestSchema(ma.Schema):
    device_name = fields.String(required=True, description='The device or service name')
    start_time = fields.String(missing="-24h", description='Start time string, either with standard ISO time format '
                                                          'or relative time like "-10s", "-30m", "-24h", "-3d"')
    end_time = fields.String(missing="0s", description='End time string, either with standard ISO time format '
                                                        'or relative time like "-20s", "-60m", "-48h", "-7d"')


# Request schema for CSV and large CSV endpoints
class CSVRequestSchema(ma.Schema):
    device_name = fields.String(required=True, description='The device or service name')
    start_time = fields.String(required=True, description='Start time string, either with standard ISO time format '
                                                          'or relative time like "-10s", "-30m", "-24h", "-3d"')
    end_time = fields.String(missing="-0s", description='End time string, either with standard ISO time format '
                                                        'or relative time like "-20s", "-60m", "-48h", "-7d"')
    frequency = fields.String(missing=None, description='frequency, sample usage as "10s", "10m", "1h", "1d"')
    iso_format = fields.Boolean(missing=False, required=False, description='return in ISO format or not')


class StreamCSVRequestSchema(ma.Schema):
    device_name = fields.String(required=True, description='The device or service name')
    start_time = fields.String(required=True, description='Start time string, either with standard ISO time format '
                                                          'or relative time like "-10s", "-30m", "-24h", "-3d"')
    end_time = fields.String(missing="-0s", description='End time string, either with standard ISO time format '
                                                        'or relative time like "-20s", "-60m", "-48h", "-7d"')
    iso_format = fields.Boolean(missing=False, required=False, description='return in ISO format or not')


# Assuming you have defined schemas for request arguments and responses
class DirectQuerySchema(Schema):
    query = fields.String(required=True, description='Flux query string')


class StreamRateSchema(Schema):
    rate = fields.String(required=True, description='Stream rate')


# For endpoints that may not require a specific input schema or have a unique input structure
# you can define them as needed. For example, for the Kafka stream:
class QueryStreamSchema(ma.Schema):
    device_name = fields.String()
    rate = fields.Int(missing=1)


class ErrorSchema(Schema):
    error = fields.Str(required=True)
