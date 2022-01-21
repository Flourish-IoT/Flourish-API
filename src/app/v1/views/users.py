from flask_restx import Resource, Namespace
from werkzeug.exceptions import NotFound

from app.common.errors.not_found_error import NotFoundError
from app.common.services.users import get_user
from app.common.models.users import UserModel

api = Namespace('users', description='User related operations', path='/users')

@api.route('/<int:user_id>')
class User(Resource):
	@api.marshal_with(UserModel)
	def get(self, user_id: int):
		try:
			user = get_user(user_id)
		except NotFoundError as e:
			raise NotFound(str(e))

		return user