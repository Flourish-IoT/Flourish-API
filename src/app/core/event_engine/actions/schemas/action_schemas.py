from marshmallow import Schema, fields, validate, post_load, validates_schema, ValidationError
from marshmallow_enum import EnumField
from app.core.models import Alert, SeverityLevelEnum
from app.common.utils import PolymorphicSchema
from ..generate_alert import GenerateAlertAction

#######################
# Schemas
#######################
class ActionSchema(PolymorphicSchema):
	action_id = fields.Int()
	disabled = fields.Bool(required=True)
	cooldown = fields.TimeDelta(required=True, allow_none=True)
	last_executed = fields.DateTime(required=True, allow_none=True)

class GenerateAlertActionSchema(ActionSchema):
	message_template = fields.Str()
	severity = EnumField(SeverityLevelEnum)

	@post_load
	def make(self, data, **kwargs):
		return GenerateAlertAction(**data)

class GenerateDeviceAlertActionSchema(ActionSchema):
	pass

class GeneratePlantAlertActionSchema(ActionSchema):
	pass

	# @post_load
	# def make(self, data, **kwargs):
	# 	return Action(**data)