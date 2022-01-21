from flask_restx import Resource, Namespace
from ...common.services.users import get_user

api = Namespace('users', description='User related operations', path='/users')

@api.route('/<int:user_id>')
class User(Resource):
	def get(self, user_id: int):
		return get_user(user_id)