import logging
from typing import List
from app.core.errors import NotFoundError, ConflictError
from app.core.models import Device
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, exc

from app.core.models import DeviceTypeEnum, DeviceStateEnum

def get_devices(user_id: int, session: ScopedSession, *, device_type: DeviceTypeEnum | None = None, device_state: DeviceTypeEnum | None = None):
	"""Gets all devices for a user

	Args:
			user_id (int): User's ID
			session (ScopedSession): SQLALchemy database session
			device_type (DeviceTypeEnum, optional): Device type to filter by. Defaults to None.
			device_state (DeviceStateEnum, optional): Device state to filter by. Defaults to None.

	Raises:
			Exception: Could not get devices for user

	Returns:
			List[Device]: User devices
	"""
	query = select(Device).where(Device.user_id == user_id)

	if device_type is not None:
		query = query.where(Device.device_type == device_type)

	if device_state is not None:
		query = query.where(Device.device_state == device_state)

	try:
		devices: List[Device] = session.execute(query).scalars().all()
	except Exception as e:
		logging.error(f'Failed to get devices for user {user_id}')
		logging.exception(e)
		raise e

	return devices

def create_device(user_id: int, device: Device, session: ScopedSession):
	"""Creates a new device and sets it's initial device state to Connecting

	Args:
			user_id (int): ID of owner
			device (Device): Device to be created
			session (ScopedSession): SQLAlchemy database session

	Raises:
			Exception: Database error

	Returns:
			int: ID of newly created device
	"""
	device.user_id = user_id
	device.device_state = DeviceStateEnum.Connecting

	try:
		session.add(device)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to create device')
		logging.exception(e)
		raise e

	return device.device_id