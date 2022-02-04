from enum import Enum
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String

class DeviceType(BaseModel):
	__tablename__ = 'device_types'

	device_type_id = Column(
		Integer,
		primary_key = True
	)
	description = Column(
		String(),
		nullable=False
	)

class DeviceTypeEnum(Enum):
	Sensor = 1,
	Gateway = 2,
	Other = 3,

	@classmethod
	def get_device_types(cls):
		"""
		Returns all valid device types
		"""
		return [e.name for e in cls]