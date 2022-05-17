from datetime import datetime
from marshmallow import fields, post_load
from app.core.models import Plant
from app.protocols.http.utils import CamelCaseSchema, DisablePostLoadMixin
from app.protocols.http.v1.schemas.plant_type_schemas import PlantTypeSchema, PlantTypeSummarySchema
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
	plant_type = fields.Nested(PlantTypeSummarySchema)
	class Meta:
		fields = ('plant_id','name', 'image', 'gauge_ratings', 'sensor_data', 'device_id', 'plant_type')

class PlantDetailsSchema(PlantSchema):
	sensor_data = fields.Nested(SensorDataSchema)
	class Meta:
		fields = ('plant_id','name', 'image', 'gauge_ratings', 'device_id', 'plant_type_id', 'plant_type', 'sensor_data')

class PlantUpdateSchema(DisablePostLoadMixin, PlantSchema):
	class Meta:
		fields = ('plant_id', 'name', 'plant_type_id', 'device_id')

class DataQuerySchema(CamelCaseSchema):
	start = fields.DateTime(default = datetime.now())
	end = fields.DateTime(default = datetime.max)
