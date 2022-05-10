from marshmallow import Schema, fields, validate, post_load
from app.protocols.http.utils import CamelCaseSchema

#######################
# Schemas
#######################
class GaugeRatingsSchema(CamelCaseSchema):
	light = fields.Int()
	temperature = fields.Int()
	humidity = fields.Int()
	soil_moisture = fields.Int()