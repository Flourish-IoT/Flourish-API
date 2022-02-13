from email.policy import default
from select import select
import string

from flask import session
from app.core.errors import NotFoundError, ConflictError
from app.core.models import User
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import exc, select, update
from typing import List
import logging

from app.core.models.plant import Plant

def get_plants(user_id: int, session: ScopedSession):
	query = select(Plant).where(Plant.user_id == user_id)

	try:
		plants: List[Plant] = session.execute(query).scalars().all()
	except Exception as e:
		logging.error(f'Failed to get plants for user')
		logging.exception(e)
		raise e

	for plant in plants:
		get_plant_target_value_ratings(plant)

	return plants

def create_plant(user_id: int, plant: Plant, session: ScopedSession):
	plant.user_id = user_id
	
	try:
		session.add(plant)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to create plant')
		logging.exception(e)
		raise e
	
	return plant.plant_id 

def get_plant_info(plant_id: int, session: ScopedSession):
	query = select(Plant).where(Plant.plant_id == plant_id)

	try:
		plant = session.get(Plant, plant_id)
	except Exception as e:
		logging.error(f'Failed to get plant info')
		logging.exception(e)
		raise e
	
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

def get_plant_sensor_data(plant_id: int, start_date: string, end_date: string, session: ScopedSession):
	pass

def get_plant_target_value_ratings(plant: Plant):
	# TODO: make this right
	if (plant.plant_type.maximum_temperature != None or plant.plant_type.minimum_temperature != None):
		#insert moks logic
		temp = 20 #replace hard coded value with actual 
		soil = 20
		light = 20
		humidity = 20

		plant.target_value_ratings['temparture'] = check_rating(temp, plant.plant_type.minimum_temperature, plant.plant_type.maximum_temperature)
		plant.target_value_ratings['soil_humidity'] = check_rating(soil, plant.plant_type.minimum_soil_moisture,plant.plant_type.maximum_soil_moisture)
		plant.target_value_ratings['light'] = check_rating(light, plant.plant_type.minimum_light, plant.plant_type.maximum_light)
		plant.target_value_ratings['humidity'] = check_rating(humidity, plant.plant_type.minimum_humidity, plant.plant_type.maximum_humidity)

def check_rating(val, min_value, max_value):
	match val:
		case n if n > min_value and n < max_value:
			return 3
		case n if n > max_value:
			return 5
		case n if n > min_value:
			return 0
			
		
		
