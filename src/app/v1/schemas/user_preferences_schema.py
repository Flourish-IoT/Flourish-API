from marshmallow import fields, post_load
from marshmallow_enum import EnumField

from app.core.models import UserPreferences, TemperatureUnitEnum
from app.v1.utils import CamelCaseSchema, DisablePostLoadMixin

class UserPreferencesSchema(CamelCaseSchema):
	temperature_unit = EnumField(TemperatureUnitEnum, required = True)

	# @post_load
	# def make(self, data, **kwargs):
	# 	return User(**data)
