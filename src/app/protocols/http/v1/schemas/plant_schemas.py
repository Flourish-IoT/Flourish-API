from typing_extensions import Required
from marshmallow import Schema, fields, validate, post_load
from marshmallow_enum import EnumField
from app.core.models import Plant, sensor_data
from app.protocols.http.utils import CamelCaseSchema, DisablePostLoadMixin
from app.protocols.http.v1.schemas.plant_type_schemas import PlantTypeSchema
from app.protocols.http.v1.schemas.gauge_ratings_schemas import GaugeRatingsSchema
from app.protocols.http.v1.schemas.sensor_data_schemas import SensorDataSchema

#######################
# Schemas
#######################
class PlantSchema(CamelCaseSchema):
	plant_id = fields.Int(data_key = 'id')
	user_id = fields.Int(required = True)
	device_id = fields.Int()
	plant_type_id = fields.Int()
	name = fields.Str()
	image = fields.Str()
	plant_type = fields.Nested(PlantTypeSchema)
	gauge_ratings = fields.Nested(GaugeRatingsSchema)

	@post_load
	def make(self, data, **kwargs):
		return Plant(**data)

class NewPlantSchema(PlantSchema):
	class Meta:
		fields = ('plant_type_id', 'name', 'image', 'device_id')

class ListPlantSchema(PlantSchema):
	sensor_data = fields.Nested(SensorDataSchema)
	class Meta:
		fields = ('plant_id','name', 'image', 'gauge_ratings', 'sensor_data')

class PlantDetailsSchema(PlantSchema):
	sensor_data = fields.Nested(SensorDataSchema)
	class Meta:
		fields = ('plant_id','name', 'image', 'gauge_ratings', 'device_id', 'plant_type_id', 'plant_type', 'sensor_data')
		
class PlantUpdateSchema(DisablePostLoadMixin, PlantSchema):
	class Meta:
		fields = ('plant_id', 'name', 'plant_type_id', 'device_id')