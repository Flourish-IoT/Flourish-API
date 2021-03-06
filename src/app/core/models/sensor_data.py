from datetime import datetime
from typing import cast
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Float, Identity
from app.core.util import With

class SensorData(BaseModel, With):
	__tablename__ = 'sensor_data'

	plant_id = cast(int, Column(
		Integer,
		ForeignKey('plants.plant_id', ondelete='CASCADE'),
		index=True,
		primary_key=True
	))

	time = cast(datetime, Column(
		TIMESTAMP(True),
		nullable=False,
		primary_key=True,
		index=True,
	))

	temperature = cast(float | None, Column(
		Float,
		nullable=True
	))

	humidity = cast(float | None, Column(
		Float,
		nullable=True
	))

	soil_moisture = cast(float | None, Column(
		Float,
		nullable=True
	))

	light = cast(int | None, Column(
		Integer,
		nullable=True
	))