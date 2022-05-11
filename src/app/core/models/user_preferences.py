from typing import cast

from .temperature_units import TemperatureUnitEnum
from .base_model import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint, Identity, text
from sqlalchemy.dialects.postgresql import INET
from .int_enum_field import IntEnumField

class UserPreferences(BaseModel):
	__tablename__ = 'user_preferences'

	user_preference_id = cast(int, Column(
		Integer,
		Identity(True),
		primary_key = True
	))

	user_id = cast(int, Column(
		Integer,
		ForeignKey('users.user_id', ondelete='CASCADE'),
	))

	temperature_unit = cast(TemperatureUnitEnum, Column(
		'temperature_unit_id',
		IntEnumField(TemperatureUnitEnum),
		ForeignKey('temperature_units.temperature_unit_id'),
		server_default=text('1')
	))

	confidence_rating = cast(int, Column(
		Integer,
		CheckConstraint('confidence_rating BETWEEN 1 and 3', name='confidence_range')
	))