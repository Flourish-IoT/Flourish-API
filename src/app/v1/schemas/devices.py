from marshmallow import Schema, fields, validate, post_load
from marshmallow_enum import EnumField
from app.core.models import Device, DeviceTypeEnum, DeviceStateEnum
from .camel_case_schema import CamelCaseSchema

#######################
# Schemas
#######################
class DeviceSchema(CamelCaseSchema):
	device_id = fields.Int(data_key = 'id')
	model = fields.Str(required = True)
	device_type = EnumField(DeviceTypeEnum, required = True)
	device_state = EnumField(DeviceStateEnum)
	user_id = fields.Int()
	name = fields.Str()
	ip = fields.IP()
	api_version = fields.Str()
	software_version = fields.Str()

	@post_load
	def make_device(self, data, **kwargs):
		return Device(**data)

class NewDeviceSchema(DeviceSchema):
	class Meta:
		fields = ('model', 'device_type', 'name', 'api_version', 'software_version')

class DeviceSummary(DeviceSchema):
	class Meta:
		fields = ('device_id', 'device_type', 'device_state', 'model', 'name')

#######################
# Mixins
#######################
class DeviceTypeQueryParamSchema(Schema):
	device_type = EnumField(DeviceTypeEnum, missing = None)

class DeviceStateQueryParamSchema(Schema):
	device_state = EnumField(DeviceStateEnum, missing = None)

#######################
# Query params
#######################
class DeviceRequestQueryParamSchema(DeviceTypeQueryParamSchema, DeviceStateQueryParamSchema):
	pass