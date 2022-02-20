from datetime import datetime
import logging
from typing import Dict, List, cast

from .value_rating import ValueRating
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .plant_type import PlantType

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

	plant_type = cast(PlantType | None, relationship("PlantType", uselist=False))

	name = cast(str, Column(
		String,
		nullable=True
	))

	image = cast(str, Column(
		String,
		nullable=True
	))

	target_value_scores: Dict[str, ValueRating] = {
		'temperature': ValueRating.NoRating,
		'light': ValueRating.NoRating,
		'humidity': ValueRating.NoRating,
		'soil_moisture': ValueRating.NoRating
	}

	def get_score_function(self, field: str):
		# TODO: get score function from db

		# default scoring functions for plants
		match field:
			case 'temperature':
				return
			case _:
				raise ValueError(f'No default score function for field {field}')
		pass

	# def get_rules(self) -> List[BaseRule]:
	# 	# cant generate rules if we don't know why kind of plant it is
	# 	if self.plant_type is None:
	# 		return []

	# 	return [
	# 		InRangeRule(self.plant_type.minimum_light, self.plant_type.maximum_light, "Light"),
	# 		InRangeRule(self.plant_type.minimum_temperature, self.plant_type.maximum_temperature, "Temperature"),
	# 		InRangeRule(self.plant_type.minimum_humidity, self.plant_type.maximum_humidity, "Humidity"),
	# 		InRangeRule(self.plant_type.minimum_soil_moisture, self.plant_type.maximum_soil_moisture, "Soil Moisture"),
	# 	]