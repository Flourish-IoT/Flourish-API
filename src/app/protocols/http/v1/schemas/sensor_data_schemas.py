from marshmallow import fields, post_load, pre_load, ValidationError
from app.core.models import SensorData
from app.protocols.http.utils import CamelCaseSchema, DisablePostLoadMixin
import datetime

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

	@pre_load
	def convert_epoch_time_to_datetime(self, data: dict, **kwargs):
		if 'timestamp' in data and not isinstance(data['timestamp'], int):
			return data

		try:
			data['timestamp'] = datetime.datetime.utcfromtimestamp(data['timestamp']).isoformat()
		except (OSError, ValueError):
			raise ValidationError("Invalid epoch time")

		return data

	@post_load
	def make(self, data: dict, **kwargs):
		# TODO: implement additional
		data.pop('additional', None)
		return SensorData(**data)