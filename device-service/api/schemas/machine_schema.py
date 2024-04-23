from marshmallow import validate, fields, validates, validates_schema, \
    ValidationError, post_dump
from api import ma, db
from api.models.machine import Machine
from api.schemas.sensor_schema import SensorSchema, DetailsURLSchema, DetailsAttributesSchema
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field


class MachineSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Machine
        ordered = True
        description = 'This schema represents a Machine'

    machine_id = fields.Int()
    machine_uuid = fields.Str()
    name = fields.Str()
    type = fields.Str()
    vendor = fields.Str()
    year = fields.Str()
    lab_name = fields.Str()
    lab_id = fields.Int()

    @validates('name')
    def validate_name(self, name):
        if len(name) < 3:
            raise ValidationError('Name must be greater than 3 characters.')
        if len(name) > 50:
            raise ValidationError('Name must be less than 50 characters.')

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if data.get('offset') is not None and data.get('after') is not None:
            raise ValidationError('Cannot specify both offset and after')


class SingleOverviewSchema(ma.Schema):
    machine_id = fields.Int()
    machine_name = fields.Str()
    overview_id = fields.Int()


class ResultSchema(ma.Schema):
    machine_id = fields.Int()
    machine_name = fields.Str()
    result_id = fields.Int()


class AllMachineSchema(ma.Schema):
    current_page = fields.Int()
    machines = fields.List(fields.Nested(MachineSchema))
    pages = fields.Int()
    total = fields.Int()


class SensorsForMachine(ma.Schema):
    sensors = fields.List(fields.Nested(SensorSchema))
    total = fields.Int()


class KeySensorsSchema(ma.Schema):
    attributes = fields.List(fields.Nested(DetailsAttributesSchema))
    category = fields.Str()
    id = fields.Int()
    name = fields.Str()
    urls = fields.Nested(DetailsURLSchema)
