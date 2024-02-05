from marshmallow import validate, fields, validates, validates_schema, \
   ValidationError, post_dump
from api import ma, db
from api.models.lab import Lab
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field


class LabURLSchema(ma.Schema):
   main = fields.Str()


class LabDetailsSchema(ma.Schema):
   machine_name = fields.Str()
   attributes = fields.List(fields.Str(), allow_none=True)
   id = fields.Int(allow_none=True)
   urls = fields.Nested(LabURLSchema)
