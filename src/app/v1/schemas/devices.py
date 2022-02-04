from marshmallow import Schema, fields, validate
from app.core.models import DeviceTypeEnum, DeviceStateEnum
from .camel_case_schema import CamelCaseSchema

#######################
# Schemas
#######################
class DeviceSchema(CamelCaseSchema):
	device_id = fields.Int(data_key = 'id')
	model = fields.Str(required = True)
	device_type = fields.Str(required = True, validate = validate.OneOf(DeviceTypeEnum.get_device_types()))
	device_state = fields.Str(validate = validate.OneOf(DeviceStateEnum.get_device_states()))
	name = fields.Str()
	ip = fields.IP()
	api_version = fields.Str()
	software_version = fields.Str()

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
	device_type = fields.Str(validate = validate.OneOf(DeviceTypeEnum.get_device_types()), missing = None)

class DeviceStateQueryParamSchema(Schema):
	device_state = fields.Str(validate = validate.OneOf(DeviceStateEnum.get_device_states()), missing = None)


#######################
# Query params
#######################
class DeviceRequestQueryParamSchema(DeviceTypeQueryParamSchema, DeviceStateQueryParamSchema):
	pass