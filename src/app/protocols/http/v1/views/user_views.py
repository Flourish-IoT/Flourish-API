import logging
from typing import Dict
from flask_restx import Resource, Namespace, Api
from flask import request, url_for
from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError, Forbidden

from app.core.errors import NotFoundError, ConflictError, ForbiddenError
from app.core.services import get_user, create_user, login, get_devices, create_device, get_alerts, edit_user, delete_user, reset_user_password, update_user_password, edit_user_preferences, start_user_reset_password, get_plants, create_plant, verify_verification_code, verify_email_password_reset_code
from app.core.services import user_service
from app.core.models import DeviceStateEnum, DeviceTypeEnum, Device, User, Plant
from app.protocols.http.v1.schemas import UserSchema, NewUserSchema, NewDeviceSchema, DeviceSummarySchema, DeviceRequestQueryParamSchema, AlertSchema, AlertRequestQueryParamSchema, UserUpdateSchema, UserPasswordUpdateSchema, AuthenticationType, UserPreferencesSchema, ResetUserPasswordSchema, ListPlantSchema, NewPlantSchema, LoginSchema, VerifySchema, UserSummarySchema, VerifyQueryParameterSchema, VerificationCodeType
from app.common.utils import marshal_with, serialize_with, marshal_list_with, Location
from app import db

from app.protocols.http.utils.authentication import authenticator, belongs_to_user

api = Namespace('users', description='User related operations', path='/users')

@api.route('')
class UserList(Resource):
	@serialize_with(NewUserSchema, strict=False)
	def post(self, body: dict):
		try:
			user_id = create_user(body['email'], body['username'], body['password'], db.session)
		except ConflictError as e:
			raise Conflict(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 201, {'Location': f'{request.path}/{user_id}'}

#  TODO: REMOVE THIS AFTER HUNTER IS DONE
	@marshal_list_with(UserSummarySchema)
	def get(self):
		try:
			users = user_service._get_users(db.session)
		except Exception as e:
			raise InternalServerError

		return users

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

@api.route('/login')
class UserLogin(Resource):
	@serialize_with(LoginSchema)
	def post(self, body: dict):
		try:
			jwt = login(body['email'], body['password'], db.session)
		except ForbiddenError as e:
			raise Forbidden(str(e))
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError
		return jwt

@api.route('/<int:user_id>/plants')
class UserPlants(Resource):
	@authenticator.login_required
	@marshal_list_with(ListPlantSchema)
	def get(self, user_id: int):
		try:
			if belongs_to_user(request, user_id):
				plants = get_plants(user_id, db.session)
			else:
				plants = None, 401, {}
		except Exception as e:
			logging.error('failed to get plants')
			logging.exception(e)
			raise InternalServerError

		return plants

	@serialize_with(NewPlantSchema)
	# @authenticator.login_required
	def post(self, user_id: int, body: Plant):
		try:
			plant_id = create_plant(user_id, body, db.session)
		except Exception as e:
			raise InternalServerError

		return None, 201, {'Location': url_for('v1.plants_plant', plant_id=plant_id)}

	@serialize_with(UserUpdateSchema)
	@authenticator.login_required
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

	@authenticator.login_required
	def delete(self, user_id: int):
		try:
			delete_user(user_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 204

@api.route('/<int:user_id>/password')
class UserPasswordUpdate(Resource):
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

@api.route('/reset_password')
class UserPassword(Resource):
	@serialize_with(ResetUserPasswordSchema)
	def post(self, body: dict):
		try:
			start_user_reset_password(body['email'], db.session)
		except ForbiddenError as e:
			raise Forbidden(str(e))
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 204

@api.route('/<int:user_id>/preferences')
class UserPreferences(Resource):
	@serialize_with(UserPreferencesSchema)
	@authenticator.login_required
	def put(self, user_id: int, body: dict):
		try:
			edit_user_preferences(user_id, body, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 204

@api.route('/<int:user_id>/devices')
class UserDevices(Resource):
	@serialize_with(DeviceRequestQueryParamSchema, location=Location.QUERY_PARAMETER)
	@marshal_list_with(DeviceSummarySchema)
	@authenticator.login_required
	def get(self, user_id: int, query: dict):
		try:
			devices = get_devices(user_id, db.session, device_type=query['device_type'], device_state=query['device_state'])
		except Exception as e:
			raise InternalServerError

		return devices

	@serialize_with(NewDeviceSchema)
	@authenticator.login_required
	def post(self, user_id: int, body: Device):
		try:
			device_id = create_device(user_id, body, db.session)
		except Exception as e:
			raise InternalServerError

		# TODO: return auth token for device
		return None, 201, {'Location': url_for('v1.devices_device_resource', device_id=device_id)}

@api.route('/<int:user_id>/alerts')
class UserAlerts(Resource):
	@serialize_with(AlertRequestQueryParamSchema, location=Location.QUERY_PARAMETER)
	@marshal_list_with(AlertSchema)
	@authenticator.login_required
	def get(self, user_id: int, query: dict):
		try:
			alerts = get_alerts(user_id, db.session, viewed=query['viewed'], plant_id=query['plant_id'], device_id=query['device_id'])
		except Exception as e:
			raise InternalServerError

		return alerts

@api.route('/verify')
class Verify(Resource):
	@serialize_with(VerifyQueryParameterSchema, location=Location.QUERY_PARAMETER)
	@serialize_with(VerifySchema)
	def post(self, body: dict, query: dict):
		try:
			code_type = query["code_type"]
			if code_type == VerificationCodeType.password_reset:
				user_id = verify_email_password_reset_code(body['email'], body['code'], db.session)
			else:
				user_id = verify_verification_code(body['email'], body['code'], db.session)
		except Exception as e:
			raise InternalServerError

		return user_id