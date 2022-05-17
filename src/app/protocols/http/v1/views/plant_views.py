import logging
from flask_restx import Resource, Namespace
from datetime import datetime
from app import db
from werkzeug.exceptions import NotFound, InternalServerError
from app.common.utils.marshal import marshal_list_with
from app.core.errors import NotFoundError
from app.protocols.http.v1.schemas import PlantDetailsSchema, PlantUpdateSchema, SensorDataSchema, DataQuerySchema
from app.common.utils import marshal_with, serialize_with, Location

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
class PlantData(Resource):
	@serialize_with(DataQuerySchema, location = Location.QUERY_PARAMETER)
	@marshal_list_with(SensorDataSchema)
	def get(self, plant_id: int, query: dict):
		try:
			data = get_plant_sensor_data(plant_id, query.get('start', datetime.now()), query.get('end', datetime.max), db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError
		
		return data