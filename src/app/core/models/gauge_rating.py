from typing import cast, Protocol
from .base_model import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, Float, Identity
from app.core.util import With

class GaugeRating(BaseModel, With):
	__tablename__ = 'gauge_ratings'

	gauge_id = cast(int, Column(
		Integer,
		Identity(True),
		primary_key=True
	))

	plant_id = cast(int, Column(
		Integer,
		ForeignKey('plants.plant_id', ondelete='CASCADE')
	))

	temperature = cast(int, Column(
		Integer,
		nullable=True
	))

	humidity = cast(int, Column(
		Integer,
		nullable=True
	))

	soil_moisture = cast(int, Column(
		Integer,
		nullable=True
	))

	light = cast(int, Column(
		Integer,
		nullable=True
	))