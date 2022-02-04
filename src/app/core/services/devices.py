import logging
from typing import List
from app.core.errors import NotFoundError, ConflictError
from app.core.models import Device
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, exc

def get_devices(user_id: int, session: ScopedSession, *, device_type: str | None = None, device_state: str | None = None):
	"""Gets all devices for a user

	Args:
			user_id (int): User's ID
			session (ScopedSession): SQLALchemy database session
			device_type (str, optional): Device type to filter by. Defaults to None.
			device_state (str, optional): Device state to filter by. Defaults to None.

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

def create_device(device: Device):
	pass