import logging
from flask import current_app as app
from flask_restx import Resource, Namespace
from sqlalchemy import delete
from app import db
from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError
from app.core.errors import NotFoundError
from app.v1.schemas import PlantDetailsSchema
from app.common.utils import marshal_with, serialize_with

from app.core.services import delete_plant, get_plant_info

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
	
	def delete(self, plant_id: int):
		try:
			delete_plant(plant_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError
		
		return None, 204