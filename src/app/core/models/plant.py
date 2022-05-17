from typing import Dict, cast
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, Identity
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from .plant_type import *
from .sensor_data import *
from .gauge_rating import *

class Plant(BaseModel):
	__tablename__ = 'plants'

	plant_id = cast(int, Column(
		Integer,
		Identity(True),
		primary_key = True,
	))

	user_id = cast(int, Column(
		Integer,
		ForeignKey('users.user_id', ondelete='CASCADE'),
		index=True
	))

	device_id = cast(int, Column(
		Integer,
		ForeignKey('devices.device_id', ondelete='SET NULL'),
	))

	plant_type_id = cast(int, Column(
		Integer,
		ForeignKey('plant_types.plant_type_id', ondelete='RESTRICT'),
		nullable = True
	))

	plant_type = cast(PlantType | None, relationship("PlantType", uselist=False))

	gauge_ratings = cast(GaugeRating | None , relationship("GaugeRating", cascade='all, delete-orphan', uselist=False) )

	name = cast(str | None, Column(
		String,
		nullable=True
	))

	image = cast(str | None, Column(
		String,
		nullable=True
	))

	sensor_data: SensorData | None


