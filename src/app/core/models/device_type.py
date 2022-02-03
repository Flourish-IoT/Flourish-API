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