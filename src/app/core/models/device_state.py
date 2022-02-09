from enum import IntEnum
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String

class DeviceState(BaseModel):
	__tablename__ = 'device_states'

	device_state_id = Column(
		Integer,
		primary_key = True
	)
	description = Column(
		String(),
		nullable=False
	)

class DeviceStateEnum(IntEnum):
	Connected = 1,
	Connecting = 2,
	Disconnected = 3,
	Error = 4,
	Unknown = 5

	@classmethod
	def get_device_states(cls):
		"""
		Returns all valid device states
		"""
		return [e.name for e in cls]