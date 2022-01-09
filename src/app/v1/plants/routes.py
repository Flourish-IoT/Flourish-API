from flask import current_app as app
from flask_restx import Resource, Namespace

api = Namespace('plants', description='Plant related operations', path='/plants')

@api.route('')
class Plant(Resource):
	def get(self):
		return 'plant get'

	def post(self):
		return 'plant post'