from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.ext.associationproxy import association_proxy

class Device(BaseModel):
	__tablename__ = 'devices'

	device_id = Column(
		Integer,
		primary_key = True
	)

	device_type_id = Column(
		Integer,
		ForeignKey('device_types.device_type_id'),
	)
	_device_type = relationship("DeviceType", )
	device_type = association_proxy('_device_type', 'description')

	device_state_id = Column(
		Integer,
		ForeignKey('device_states.device_state_id'),
	)
	_device_state = relationship("DeviceState")
	device_state = association_proxy('_device_state', 'description')

	user_id = Column(
		Integer,
		ForeignKey('users.user_id'),
	)

	ip = Column(
		INET,
		nullable=True
	)
	api_version = Column(
		String,
		nullable=True
	)
	software_version = Column(
		String,
		nullable=True
	)
	model = Column(
		String,
		nullable=True
	)
	name = Column(
		String,
		nullable=True
	)