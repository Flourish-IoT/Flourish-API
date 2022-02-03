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