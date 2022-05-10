from attr import field
from marshmallow import Schema, fields, validate, post_load
from marshmallow_enum import EnumField
from app.core.models import PlantType
from app.protocols.http.utils import CamelCaseSchema, DisablePostLoadMixin

#######################
# Schemas
#######################
class PlantTypeSchema(CamelCaseSchema):
	plant_type_id = fields.Int(data_key = 'id')
	scientific_name = fields.Str()
	minimum_light = fields.Int()
	maximum_light = fields.Int()
	minimum_temperature = fields.Float()
	maximum_temperature = fields.Float()
	minimum_humidity = fields.Float()
	maximum_humidity = fields.Float()
	minimum_soil_moisture = fields.Float()
	maximum_soil_moisture = fields.Float()
	image = fields.Str()

	@post_load
	def make(self, data, **kwargs):
		return PlantType(**data)

class PlantTypeSummarySchema(PlantTypeSchema):
	class Meta:
		fields = ('plant_type_id', 'scientific_name',)


