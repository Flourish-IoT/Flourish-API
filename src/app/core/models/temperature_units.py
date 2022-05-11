from enum import IntEnum

from app.core.util import EnumValuesMixin
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, Identity

class TemperatureUnits(BaseModel):
	__tablename__ = 'temperature_units'

	temperature_unit_id = Column(
		Integer,
		Identity(True),
		primary_key = True
	)
	unit = Column(
		String(),
		nullable=False
	)

class TemperatureUnitEnum(EnumValuesMixin, IntEnum):
	Fahrenheit = 1,
	Celcius = 2,