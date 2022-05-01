import logging
from typing import List
from app.core.errors import NotFoundError, ConflictError
import app.core.event_engine as event_engine
import app.core.event_engine.events as events
from app.core.models import Device, Plant, DeviceTypeEnum, DeviceStateEnum, SensorData, GaugeRating
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, exc, update, exists

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
	plant_query = select(Plant).where(Plant.device_id == device_id)

	try:
		plants: List[Plant] = session.execute(plant_query).scalars().all()
	except exc.DatabaseError as e:
		logging.error('Failed to update device')
		logging.exception(e)
		raise e

	if len(plants) == 0:
		logging.info(f'No plants associated with device {device_id}. Data will not be recorded')
		# TODO: return state
		return

	logging.info(f'Recording sensor data for {len(plants)} plants: {plants}')

	# record values in table for each plant
	sensor_data = [data.with_value(SensorData.plant_id, plant.plant_id) for plant in plants]

	for plant in plants:
		if plant.gauge_ratings is None:
			plant.gauge_ratings = GaugeRating()
		get_plant_gauge_ratings(plant, data)
	

	try:
		session.bulk_save_objects(sensor_data)
		session.add_all(plants)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to insert data')
		logging.exception(e)
		raise e

	# run event handlers for each plant
	for plant, sensor_data in zip(plants, sensor_data):
		event_engine.handle(events.SensorDataEvent(user_id=plant.user_id, plant=plant, data=sensor_data, session=session))

	# return state

def device_exists(device_id: int, session: ScopedSession) -> bool:
	"""Checks if a device with given device_id exists
	Args:
			device_id (int): Device ID to check for
			session (ScopedSession): SQLAlchemy database session
	Returns:
		bool: Represents whether device exists
	"""
	return session.query(exists(Device).where(Device.device_id == device_id)).scalar()

def get_plant_gauge_ratings(plant: Plant, sensor_data: SensorData):
	# TODO: make this right
	# if (plant.plant_type.maximum_temperature != None or plant.plant_type.minimum_temperature != None):
		#insert moks logic
	if plant.plant_type is None or sensor_data is None or plant.gauge_ratings is None:
		return
		
	plant.gauge_ratings.temperature = check_rating(sensor_data.temperature , plant.plant_type.minimum_temperature, plant.plant_type.maximum_temperature)
	plant.gauge_ratings.soil_moisture = check_rating(sensor_data.soil_moisture, plant.plant_type.minimum_soil_moisture,plant.plant_type.maximum_soil_moisture)
	plant.gauge_ratings.light = check_rating(sensor_data.light, plant.plant_type.minimum_light, plant.plant_type.maximum_light)
	plant.gauge_ratings.humidity = check_rating(sensor_data.humidity, plant.plant_type.minimum_humidity, plant.plant_type.maximum_humidity)

def check_rating(val, min_value, max_value):
	#If its is below the min value, return 1 and above max value, return 5
	#Split the range into 3 and return 2,3,4 appropriately
	range = max_value - min_value
	rating = val-min_value

	if (rating <= 0):
		return 1
	elif (rating >= range):
		return 5


	if(rating <= range/3):
		return 2
	elif(rating >= range * 2 / 3):
		return 4
	else:
		return 3