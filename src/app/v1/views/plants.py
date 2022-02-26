import logging
from flask import current_app as app
from flask_restx import Resource, Namespace
from sqlalchemy import delete
from app import db
from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError
from app.core.errors import NotFoundError
from app.v1.schemas import PlantDetailsSchema, PlantUpdateSchema, PlantSensorDataSchema
from app.common.utils import marshal_with, serialize_with

from app.core.services import delete_plant, get_plant_info, edit_plant_info, get_plant_sensor_data

api = Namespace('plants', description='Plant related operations', path='/plants')

@api.route('/<int:plant_id>')
class Plant(Resource):
	@marshal_with(PlantDetailsSchema)
	def get(self, plant_id):
		try:
			plant = get_plant_info(plant_id, db.session)
		except Exception as e:
			logging.error('failed to get plant info')
			logging.exception(e)
			raise InternalServerError
		
		return plant

	def post(self):
		return 'plant post'
	
	@serialize_with(PlantUpdateSchema)
	def put(self, plant_id: int, body: dict):
		try:
			edit_plant_info(plant_id, body, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError
		
		return None, 204
	
	def delete(self, plant_id: int):
		try:
			delete_plant(plant_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError
		
		return None, 204

@api.route('/<int:plant_id>/data')
class Plant(Resource):
	@marshal_with(PlantSensorDataSchema)
	def get(self, plant_id, start_date, end_date):
		try:
			data = get_plant_sensor_data(plant_id, start_date, end_date, db.session)
		except Exception as e:
			logging.error('failed to get plant sensor data')
			logging.exception(e)
			raise e

		return data