from marshmallow import Schema, fields, validate, post_load, validates_schema, ValidationError
from marshmallow_enum import EnumField
from app.core.models import Alert, SeverityLevelEnum
from app.v1.utils import CamelCaseSchema, DisablePostLoadMixin

#######################
# Schemas
#######################
class AlertSchema(CamelCaseSchema):
	alert_id = fields.Int(data_key = 'id')
	plant_id = fields.Int()
	device_id = fields.Int()
	user_id = fields.Int()
	severity = EnumField(SeverityLevelEnum)
	time = fields.DateTime()
	viewed = fields.Bool()

	# @post_load
	# def make(self, data, **kwargs):
	# 	return Device(**data)

class AlertViewRequestSchema(CamelCaseSchema):
	viewed = fields.Bool(required=True)
	alert_ids = fields.List(fields.Int())

#######################
# Mixins
#######################
class ViewedQueryParamSchema(Schema):
	viewed = fields.Bool(missing=None)

class PlantIdQueryParamSchema(Schema):
	plant_id = fields.Int(missing=None)

class DeviceIdQueryParamSchema(Schema):
	device_id = fields.Int(missing=None)


#######################
# Query params
#######################
class AlertRequestQueryParamSchema(ViewedQueryParamSchema, PlantIdQueryParamSchema, DeviceIdQueryParamSchema):
	@validates_schema
	def validate_schema(self, data: dict, **kwargs):
		if (data.get('plant_id') is not None and data.get('device_id') is not None):
			raise ValidationError('plant_id and device_id cannot be used together')