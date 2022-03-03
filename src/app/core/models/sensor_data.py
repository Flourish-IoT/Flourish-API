from datetime import datetime
from typing import cast, Protocol
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Float
from sqlalchemy.dialects.postgresql import INET
from app.core.util import With

class SensorData(BaseModel, With):
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