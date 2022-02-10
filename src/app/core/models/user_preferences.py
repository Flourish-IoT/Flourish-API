from typing import cast

from .temperature_units import TemperatureUnitEnum
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from .int_enum_field import IntEnumField

class UserPreferences(BaseModel):
	__tablename__ = 'user_preferences'

	user_preference_id = cast(int, Column(
		Integer,
		primary_key = True
	))

	user_id = cast(int, Column(
		Integer,
		ForeignKey('users.user_id'),
	))

	temperature_unit = cast(TemperatureUnitEnum, Column(
		'temperature_unit_id',
		IntEnumField(TemperatureUnitEnum),
		ForeignKey('temperature_units.temperature_unit_id'),
		default=TemperatureUnitEnum.Fahrenheit
	))