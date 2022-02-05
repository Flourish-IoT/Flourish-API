from datetime import datetime
from typing import cast
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Float
from sqlalchemy.dialects.postgresql import INET
from .int_enum_field import IntEnumField
from .device_type import DeviceTypeEnum
from .device_state import DeviceStateEnum

class SensorData(BaseModel):
	__tablename__ = 'sensor_data'

	plant_id = cast(int, Column(
		Integer,
		primary_key = True
	))

	time = cast(datetime, Column(
		TIMESTAMP
	))

	temperature = cast(float, Column(
		Float,
		nullable=True
	))

	humidity = cast(float, Column(
		Float,
		nullable=True
	))

	soil_moisture = cast(float, Column(
		Float,
		nullable=True
	))

	light = cast(int, Column(
		Integer,
		nullable=True
	))