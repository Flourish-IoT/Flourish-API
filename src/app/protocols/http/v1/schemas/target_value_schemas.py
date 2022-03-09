from marshmallow import Schema, fields, validate, post_load
from app.protocols.http.utils import CamelCaseSchema

#######################
# Schemas
#######################
class TargetValueSchema(CamelCaseSchema):
	light = fields.Int()
	temperature = fields.Int()
	humidity = fields.Int()
	soil_moisture = fields.Int()