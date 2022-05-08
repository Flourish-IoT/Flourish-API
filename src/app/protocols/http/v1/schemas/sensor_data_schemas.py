from marshmallow import fields, post_load
from app.core.models import SensorData
from app.protocols.http.utils import CamelCaseSchema, DisablePostLoadMixin

#######################
# Schemas
#######################
class SensorDataSchema(CamelCaseSchema):
	time = fields.DateTime(data_key = 'timestamp')
	temperature = fields.Float()
	humidity = fields.Float()
	soil_moisture = fields.Float()
	light = fields.Integer()
	additional = fields.Dict()

	@post_load
	def make(self, data: dict, **kwargs):
		# TODO: implement additional
		data.pop('additional', None)
		return SensorData(**data)