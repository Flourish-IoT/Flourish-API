from select import select
import string

from flask import session
from app.core.errors import NotFoundError, ConflictError
from app.core.models import User
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import exc, select
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

	pass

def edit_plant_info(plant_id: int, session: ScopedSession):
	pass

def delete_plant(plant_id: int, session: ScopedSession):
	plant = session.get(Plant, plant_id)
	
	if plant is None:
		raise NotFoundError(f'Could not find plant with id: {plant_id}')

	try:
		session.delete(selected_plant)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to delete plant')
		logging.exception(e)
		raise e

def get_plant_sensor_data(plant_id: int, start_date: string, end_date: string, session: ScopedSession):
	pass

