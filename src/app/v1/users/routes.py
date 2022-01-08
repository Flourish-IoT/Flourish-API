from flask import current_app as app
from flask_restx import Resource, Namespace

api = Namespace('users', description='User related operations', path='/users')

@api.route('/')
class User(Resource):
	def get(self):
		return 'foo'