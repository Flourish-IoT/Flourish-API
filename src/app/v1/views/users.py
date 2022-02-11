import logging
from typing import Dict
from flask_restx import Resource, Namespace, Api
from flask import request, url_for
from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError, Forbidden

from app.core.errors import NotFoundError, ConflictError, ForbiddenError
from app.core.services import get_user, create_user, get_devices, create_device, get_alerts, edit_user, delete_user, reset_user_password, update_user_password
from app.core.models import DeviceStateEnum, DeviceTypeEnum, Device, User
from app.v1.schemas import UserSchema, NewUserSchema, NewDeviceSchema, DeviceSummarySchema, DeviceRequestQueryParamSchema, AlertSchema, AlertRequestQueryParamSchema, UserUpdateSchema, UserPasswordUpdateSchema, AuthenticationType
from app.common.utils import marshal_with, serialize_with, marshal_list_with, Location
from app import db

api = Namespace('users', description='User related operations', path='/users')

@api.route('')
class UserList(Resource):
	@serialize_with(NewUserSchema, strict=False)
	def post(self, body: dict):
		try:
			user_id = create_user(body['email'], db.session)
		except ConflictError as e:
			raise Conflict(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 201, {'Location': f'{request.path}/{user_id}'}

@api.route('/<int:user_id>')
class UserResource(Resource):
	@marshal_with(UserSchema)
	def get(self, user_id: int):
		try:
			user = get_user(user_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return user

	@serialize_with(UserUpdateSchema)
	def put(self, user_id: int, body: dict):
		try:
			edit_user(user_id, body, db.session)
		except ConflictError as e:
			raise Conflict(str(e))
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 204

	def delete(self, user_id: int):
		try:
			delete_user(user_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 204

@api.route('/<int:user_id>/password')
class UserPassword(Resource):
	@serialize_with(UserPasswordUpdateSchema)
	def put(self, user_id: int, body: dict):
		try:
			if body['authentication_type'] == AuthenticationType.password:
				# password update
				update_user_password(user_id, body['authentication'], body['new_password'], db.session)
			else:
				# password reset
				reset_user_password(user_id, body['authentication'], body['new_password'], db.session)
		except ForbiddenError as e:
			raise Forbidden(str(e))
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 204

@api.route('/<int:user_id>/devices')
class UserDevices(Resource):
	@serialize_with(DeviceRequestQueryParamSchema, location=Location.QUERY_PARAMETER)
	@marshal_list_with(DeviceSummarySchema)
	def get(self, user_id: int, query: dict):
		try:
			devices = get_devices(user_id, db.session, device_type=query['device_type'], device_state=query['device_state'])
		except Exception as e:
			raise InternalServerError

		return devices

	@serialize_with(NewDeviceSchema)
	def post(self, user_id: int, body: Device):
		try:
			device_id = create_device(user_id, body, db.session)
		except Exception as e:
			raise InternalServerError

		# TODO: return auth token for device
		return None, 201, {'Location': url_for('v1.devices_device', device_id=device_id)}

@api.route('/<int:user_id>/alerts')
class UserAlerts(Resource):
	@serialize_with(AlertRequestQueryParamSchema, location=Location.QUERY_PARAMETER)
	@marshal_list_with(AlertSchema)
	def get(self, user_id: int, query: dict):
		try:
			alerts = get_alerts(user_id, db.session, viewed=query['viewed'], plant_id=query['plant_id'], device_id=query['device_id'])
		except Exception as e:
			raise InternalServerError

		return alerts