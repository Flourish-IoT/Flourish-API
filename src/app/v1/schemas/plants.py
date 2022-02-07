from marshmallow import Schema, fields, validate, post_load
from marshmallow_enum import EnumField
from app.core.models import Plant
from app.v1.utils import CamelCaseSchema, DisablePostLoadMixin

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

	@post_load
	def make(self, data, **kwargs):
		return Plant(**data)

class NewPlantSchema(PlantSchema):
	class Meta:
		fields = ('plant_type_id', 'name', 'image', 'device_id')

# class DeviceSummarySchema(DeviceSchema):
# 	class Meta:
# 		fields = ('device_id', 'device_type', 'device_state', 'model', 'name')

# class DeviceUpdateSchema(DisablePostLoadMixin, DeviceSchema):
# 	class Meta:
# 		fields = ('model', 'device_type', 'name', 'api_version', 'software_version')
# 	model = fields.Str(required = False)
# 	device_type = EnumField(DeviceTypeEnum, required = False)


#######################
# Mixins
#######################
# class DeviceTypeQueryParamSchema(Schema):
# 	device_type = EnumField(DeviceTypeEnum, missing = None)

# class DeviceStateQueryParamSchema(Schema):
# 	device_state = EnumField(DeviceStateEnum, missing = None)

#######################
# Query params
#######################
# class DeviceRequestQueryParamSchema(DeviceTypeQueryParamSchema, DeviceStateQueryParamSchema):
# 	pass