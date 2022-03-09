from marshmallow import fields, post_load, validate
from marshmallow_enum import EnumField

from app.core.models import UserPreferences, TemperatureUnitEnum
from app.protocols.http.utils import CamelCaseSchema, DisablePostLoadMixin

class UserPreferencesSchema(CamelCaseSchema):
	temperature_unit = EnumField(TemperatureUnitEnum, required = True)
	confidence_rating = fields.Int(validate=validate.Range(1, 3), required=True)

	# @post_load
	# def make(self, data, **kwargs):
	# 	return User(**data)
