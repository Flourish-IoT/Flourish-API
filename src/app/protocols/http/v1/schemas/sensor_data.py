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

	@post_load
	def make(self, data, **kwargs):
		return SensorData(**data)
