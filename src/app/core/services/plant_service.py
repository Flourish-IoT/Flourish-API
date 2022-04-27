from email.policy import default
import string

from flask import session
from app.core.errors import NotFoundError, ConflictError
from app.core.models import Plant, SeverityLevelEnum, Alert, ValueRating, SensorData
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import exc, select, update
from typing import List
from datetime import datetime
import logging
import app.core.event_engine as event_engine
import app.core.services.event_handler_service as event_handler_service

def get_plants(user_id: int, session: ScopedSession):
	query = select(Plant).where(Plant.user_id == user_id)

	try:
		plants: List[Plant] = session.execute(query).scalars().all()
	except Exception as e:
		logging.error(f'Failed to get plants for user')
		logging.exception(e)
		raise e

	for plant in plants:
		if plant is None:
			raise NotFoundError(f'Could not find plant with ID: {plant.plant_id}')

		sensor_query = select(SensorData).where(SensorData.plant_id == plant.plant_id).order_by(SensorData.time.desc()).limit(1) # type: ignore

		try: 
			value: SensorData | None = session.execute(sensor_query).scalar_one_or_none()
		except exc.DatabaseError as e:
			logging.error('Failed to create plant')
			logging.exception(e)
			raise e

		plant.sensor_data = value
		get_plant_target_value_ratings(plant)

	return plants

def create_plant(user_id: int, plant: Plant, session: ScopedSession):
	plant.user_id = user_id

	try:
		session.add(plant)
		session.flush()
	except exc.DatabaseError as e:
		logging.error('Failed to create plant')
		logging.exception(e)
		raise e

	event_handlers = event_engine.generate_default_plant_event_handlers()

	try:
		for event_handler in event_handlers:
			event_handler_service.create_event_handler(event_handler, session, plant_id=plant.plant_id, auto_commit=False)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to create plant event handlers')
		logging.exception(e)
		raise e

	return plant.plant_id

def get_plant_info(plant_id: int, session: ScopedSession):
	plant = session.get(Plant, plant_id)

	if plant is None:
		raise NotFoundError(f'Could not find plant with ID: {plant_id}')

	sensor_query = select(SensorData).where(SensorData.plant_id == plant_id).order_by(SensorData.time.desc()).limit(1) # type: ignore

	try: 
		value: SensorData | None = session.execute(sensor_query).scalar_one_or_none()
	except exc.DatabaseError as e:
		logging.error('Failed to create plant')
		logging.exception(e)
		raise e

	plant.sensor_data = value
	get_plant_target_value_ratings(plant)
	
	return plant

def edit_plant_info(plant_id: int, plant_update: dict, session: ScopedSession):
	try:
		session.execute(
			update(Plant)
				.where(Plant.plant_id == plant_id)
				.values(**plant_update)
		)
		session.commit()
	except exc.NoResultFound as e:
		logging.error('Failed to find plant')
		logging.exception(e)
		raise NotFoundError(f'Could not find plant with id: {plant_id}')
	except exc.DatabaseError as e:
		logging.error('Failed to update plant')
		logging.exception(e)
		raise e

def delete_plant(plant_id: int, session: ScopedSession):
	plant = session.get(Plant, plant_id)
	if plant is None:
		raise NotFoundError(f'Could not find plant with id: {plant_id}')

	try:
		session.delete(plant)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to delete plant')
		logging.exception(e)
		raise e

def get_plant_sensor_data(plant_id: int, start_date: str, end_date: str, session: ScopedSession):
	pass

def get_last_plant_sensor_data(plant: Plant, plant_id: int, session: ScopedSession):
	query = select(SensorData).where(SensorData.plant_id == plant_id)
	query = query.limit(1)

	try:
		value = session.execute(query).scalar_one()
		print(value)
	except exc.DatabaseError as e:
		logging.error('Failed to execute query')
		logging.exception(e)
		return None

	logging.info(f'Latest value: {value}')

	return value

def get_plant_target_value_ratings(plant: Plant):
	# TODO: make this right
	# if (plant.plant_type.maximum_temperature != None or plant.plant_type.minimum_temperature != None):
		#insert moks logic
	if plant.plant_type is None or plant.sensor_data is None:
		return
		
	plant.target_value_ratings['temperature'] = check_rating(plant.sensor_data.temperature, plant.plant_type.minimum_temperature, plant.plant_type.maximum_temperature)
	plant.target_value_ratings['soil_moisture'] = check_rating(plant.sensor_data.soil_moisture, plant.plant_type.minimum_soil_moisture,plant.plant_type.maximum_soil_moisture)
	plant.target_value_ratings['light'] = check_rating(plant.sensor_data.light, plant.plant_type.minimum_light, plant.plant_type.maximum_light)
	plant.target_value_ratings['humidity'] = check_rating(plant.sensor_data.humidity, plant.plant_type.minimum_humidity, plant.plant_type.maximum_humidity)

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




