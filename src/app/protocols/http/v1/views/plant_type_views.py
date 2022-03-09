from flask import current_app as app
from flask_restx import Resource, Namespace
from app import db
from app.core.errors.not_found_error import NotFoundError
from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError
from app.core.errors import NotFoundError
from app.protocols.http.v1.schemas import PlantTypeSchema

from app.core.services import get_all_plant_types, get_plant_type
from app.common.utils.marshal import marshal_with, marshal_list_with

api = Namespace('plant_types', description='Plant Type related operations', path='/plant_types')

@api.route('/<int:plant_type_id>')
class PlantTypeResource(Resource):
	@marshal_with(PlantTypeSchema)
	def get(self, plant_type_id):
		try:
			plant_type = get_plant_type(plant_type_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return plant_type

	def post(self):
		return 'plant type post'

@api.route('')
class PlantTypeListResource(Resource):
	@marshal_list_with(PlantTypeSchema)
	def get(self):
		try:
			plant_types = get_all_plant_types(db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return plant_types


	def post(self):
		return 'plant type post'