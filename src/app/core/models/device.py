from typing import cast
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.ext.associationproxy import association_proxy
from .int_enum_field import IntEnumField
from .device_type import DeviceTypeEnum
from .device_state import DeviceStateEnum

class Device(BaseModel):
	__tablename__ = 'devices'

	device_id = cast(int, Column(
		Integer,
		primary_key = True
	))

	model = cast(str, Column(
		String,
		nullable=False
	))

	device_type = cast(DeviceTypeEnum, Column(
		'device_type_id',
		IntEnumField(DeviceTypeEnum),
		ForeignKey('device_types.device_type_id')
	))

	device_state = cast(DeviceStateEnum, Column(
		'device_state_id',
		IntEnumField(DeviceStateEnum),
		ForeignKey('device_states.device_state_id'),
		default=DeviceStateEnum.Unknown
	))

	user_id = cast(int, Column(
		Integer,
		ForeignKey('users.user_id'),
	))

	ip = cast(str, Column(
		INET,
		nullable=True
	))
	api_version = cast(str, Column(
		String,
		nullable=True
	))
	software_version = cast(str, Column(
		String,
		nullable=True
	))
	name = cast(str, Column(
		String,
		nullable=True
	))