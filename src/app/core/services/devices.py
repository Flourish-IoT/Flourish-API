import logging
from typing import List
from app.core.errors import NotFoundError, ConflictError
from app.core.models import Device
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, exc, update

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

def get_device(device_id: int, session: ScopedSession):
	"""Gets a device by device ID

	Args:
			device_id (int): ID of the device

	Raises:
			NotFoundError: Device not found

	Returns:
			Device
	"""
	device = session.get(Device, device_id)

	if device is None:
		raise NotFoundError(f'Could not find device with id: {device_id}')

	return device


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

def edit_device(device_id: int, device_update: dict, session: ScopedSession):
	"""Edits device information

	Args:
			device_id (int): ID of device being edited
			device_update (dict): Updated fields of device. Keys must match field names of Device
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: Device not found
			Exception: Database error
	"""
	try:
		session.execute(
			update(Device)
				.where(Device.device_id == device_id)
				.values(**device_update)
		)
		session.commit()
	except exc.NoResultFound as e:
		logging.error('Failed to find device')
		logging.exception(e)
		raise NotFoundError(f'Could not find device with id: {device_id}')
	except exc.DatabaseError as e:
		logging.error('Failed to update device')
		logging.exception(e)
		raise e

def delete_device(device_id: int, session: ScopedSession):
	"""Deletes device

	Args:
			device_id (int): ID of device being deleted
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: Device not found
			Exception: Database error
	"""
	device = get_device(device_id, session)

	try:
		session.delete(device)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to delete device')
		logging.exception(e)
		raise e

def record_data(device_id: int, data, session: ScopedSession):
	# get all plants associated with device
	plant_ids = select(Plant)

	# record values in table for each plant

	# perform checks for each plant

	# generate alerts

	# return state
	pass