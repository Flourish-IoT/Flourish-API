import logging
from flask_restx import Resource, Namespace, reqparse
from flask import request
from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError

from app.core.errors import NotFoundError, ConflictError
from app.core.services import get_user, create_user, get_devices
from app.v1.models import NewUserModel, UserModel, DeviceModel
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
		# TODO: query param
		try:
			user = get_user(user_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			logging.error('Failed to create user')
			logging.exception(e)
			raise InternalServerError

		return user

device_parser = reqparse.RequestParser()
device_parser.add_argument('device_type_id', type=int, location='args')
device_parser.add_argument('device_state_id', type=int, location='args')
@api.route('/<int:user_id>/devices')
class UserDevices(Resource):
	@api.expect(device_parser, strict=True)
	@api.marshal_list_with(DeviceModel)
	def get(self, user_id: int):
		args = device_parser.parse_args(strict=True)

		try:
			devices = get_devices(user_id, db.session, device_type_id=args['device_type_id'], device_state_id=args['device_state_id'])
		except Exception as e:
			logging.error('Failed to get user devices')
			logging.exception(e)
			raise InternalServerError

		return devices

	def post(self, user_id: int):
		pass