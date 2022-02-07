from flask import current_app as app
from flask_restx import Resource, Namespace
from sqlalchemy import delete
from app import db
from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError
from app.core.errors import NotFoundError

from app.core.services import delete_plant

api = Namespace('plants', description='Plant related operations', path='/plants')

@api.route('/<int:plant_id>')
class Plant(Resource):
	def get(self):
		return 'plant get'

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