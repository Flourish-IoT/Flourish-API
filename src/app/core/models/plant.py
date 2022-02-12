from typing import Dict, cast
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from .plant_type import *

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

	target_value_ratings: Dict[str, int] = {'temperature': None , 'light': None, 'humidity': None, 'soil_moisture': None}

	
