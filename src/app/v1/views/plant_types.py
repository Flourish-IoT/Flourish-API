from flask import current_app as app
from flask_restx import Resource, Namespace

api = Namespace('plant_types', description='Plant Type related operations', path='/plant_types')

@api.route('/<int:plant_type_id>')
class PlantType(Resource):
	def get(self, plant_type_id):
		return 'plant type get'

	def post(self):
		return 'plant type post'

@api.route('')
class PlantType(Resource):
	def get(self):
		return 'plant type get'

	def post(self):
		return 'plant type post'