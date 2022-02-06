from typing import cast
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from .int_enum_field import IntEnumField
from .device_type import DeviceTypeEnum
from .device_state import DeviceStateEnum

class Plant(BaseModel):
	__tablename__ = 'plants'

	plant_id = cast(int, Column(
		Integer,
		primary_key = True
	))

	user_id = cast(int, Column(
		Integer,
		ForeignKey('users.user_id'),
	))

	device_id = cast(int, Column(
		Integer,
		ForeignKey('devices.device_id'),
	))

	plant_type_id = cast(int, Column(
		Integer,
		ForeignKey('plant_types.plant_type_id'),
	))

	name = cast(str, Column(
		String,
		nullable=True
	))

	image = cast(str, Column(
		String,
		nullable=True
	))
