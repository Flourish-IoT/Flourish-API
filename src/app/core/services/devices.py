import logging
from typing import List
from app.core.errors import NotFoundError, ConflictError
from app.core.models import Device, Plant
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, exc, update, exists

from app.core.models import DeviceTypeEnum, DeviceStateEnum, SensorData

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
	logging.info(f'Getting devices for user {user_id}')
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
	logging.info(f'Getting device information for device {device_id}')
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
	logging.info(f'Creating device for user {user_id}')
	device.user_id = user_id
	device.device_state = DeviceStateEnum.Connecting

	try:
		session.add(device)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to create device')
		logging.exception(e)
		raise e

	logging.info(f'Succesfully created device {device.device_id} for user {user_id}')
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
	logging.info(f'Editing device {device_id}')
	if not device_exists(device_id, session):
		logging.error('Could not find device')
		raise NotFoundError(f'Could not find device with id: {device_id}')

	try:
		session.execute(
			update(Device)
				.where(Device.device_id == device_id)
				.values(**device_update)
		)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to update device')
		logging.exception(e)
		raise e

	logging.info(f'Succesfully edited device {device_id}')

def delete_device(device_id: int, session: ScopedSession):
	"""Deletes device

	Args:
			device_id (int): ID of device being deleted
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: Device not found
			Exception: Database error
	"""
	logging.info(f'Deleting device {device_id}')
	device = get_device(device_id, session)

	try:
		session.delete(device)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to delete device')
		logging.exception(e)
		raise e

	logging.info(f'Succesfully deleted device {device_id}')

def record_data(device_id: int, data: SensorData, session: ScopedSession):
	logging.info(f'Recording sensor data for device {device_id}')
	# TODO: return state update

	# get all plants associated with device
	plant_query = select(Plant.plant_id).where(Plant.device_id == device_id)

	try:
		plant_ids: List[int] = session.execute(plant_query).scalars().all()
	except exc.DatabaseError as e:
		logging.error('Failed to update device')
		logging.exception(e)
		raise e

	if len(plant_ids) == 0:
		logging.info(f'No plants associated with device {device_id}. Data will not be recorded')
		# TODO: return state
		return

	logging.info(f'Recording sensor data for {len(plant_ids)} plants: {plant_ids}')

	# record values in table for each plant
	sensor_data = list(map(lambda plant_id: data.with_value(SensorData.plant_id, plant_id), plant_ids))

	try:
		session.bulk_save_objects(sensor_data)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to insert data')
		logging.exception(e)
		raise e

	# perform checks for each plant

	# generate alerts

	# return state
	pass

def device_exists(device_id: int, session: ScopedSession) -> bool:
	"""Checks if a device with given device_id exists
	Args:
			device_id (int): Device ID to check for
			session (ScopedSession): SQLAlchemy database session
	Returns:
		bool: Represents whether device exists
	"""
	return session.query(exists(Device).where(Device.device_id == device_id)).scalar()