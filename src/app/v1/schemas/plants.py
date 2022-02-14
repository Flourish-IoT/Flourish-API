from typing_extensions import Required
from marshmallow import Schema, fields, validate, post_load
from marshmallow_enum import EnumField
from app.core.models import Plant
from app.v1.utils import CamelCaseSchema, DisablePostLoadMixin
from app.v1.schemas.plant_types import PlantTypeSchema
from app.v1.schemas.target_value import TargetValueSchema

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
	target_value_ratings = fields.Nested(TargetValueSchema)

	@post_load
	def make(self, data, **kwargs):
		return Plant(**data)

class NewPlantSchema(PlantSchema):
	class Meta:
		fields = ('plant_type_id', 'name', 'image', 'device_id')

class ListPlantSchema(PlantSchema):
	class Meta:
		fields = ('plant_id','name', 'image', 'target_value_ratings')

class PlantDetailsSchema(PlantSchema):
	class Meta:
		fields = ('plant_id','name', 'image', 'target_value_ratings', 'device_id', 'plant_type_id', 'plant_type')

class PlantUpdateSchema(DisablePostLoadMixin, PlantSchema):
	class Meta:
		fields = ('plant_id', 'name', 'plant_type_id', 'device_id')