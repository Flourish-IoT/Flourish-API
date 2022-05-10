from typing import Dict, cast
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from .plant_type import *
from .sensor_data import *
from .gauge_rating import *

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
		nullable = True
	))

	plant_type = cast(PlantType | None, relationship("PlantType", uselist=False))

	gauge_ratings = cast(GaugeRating | None , relationship("GaugeRating", cascade='all, delete-orphan', uselist=False) )

	name = cast(str, Column(
		String,
		nullable=True
	))

	image = cast(str, Column(
		String,
		nullable=True
	))

	# target_value_scores: Dict[str, ValueRating] = {
	# 	'temperature': ValueRating.NoRating,
	# 	'light': ValueRating.NoRating,
	# 	'humidity': ValueRating.NoRating,
	# 	'soil_moisture': ValueRating.NoRating
	# }

	def get_score_function(self, field: str):
		# TODO: get score function from db

		# default scoring functions for plants
		match field:
			case 'temperature':
				return
			case _:
				raise ValueError(f'No default score function for field {field}')
		pass

	sensor_data: SensorData | None


