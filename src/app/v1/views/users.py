import logging
from flask_restx import Resource, Namespace
from flask import request
from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError

from app.core.errors import NotFoundError, ConflictError
from app.core.services import get_user, create_user
from app.v1.models import NewUserModel, UserModel
from app import db

api = Namespace('users', description='User related operations', path='/users')
api.add_model('User', UserModel)
api.add_model('NewUser', NewUserModel)

@api.route('')
class UserList(Resource):
	@api.expect(NewUserModel, validate=True)
	def post(self):
		body = request.get_json()
		if body is None:
			raise BadRequest

		try:
			user_id = create_user(body['email'], db.session)
		except ConflictError as e:
			raise Conflict(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 201, {'Location': f'{request.path}/{user_id}'}

@api.route('/<int:user_id>')
class User(Resource):
	@api.marshal_with(UserModel)
	def get(self, user_id: int):
		try:
			user = get_user(user_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			logging.error('Failed to create user')
			logging.exception(e)
			raise InternalServerError

		return user