import logging
from typing import Dict
from flask_restx import Resource, Namespace, Api
from flask import request, url_for
from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError

from app.core.errors import NotFoundError, ConflictError
from app.core.services import get_user, create_user, get_devices, create_device
from app.core.models import DeviceStateEnum, DeviceTypeEnum, Device, User
from app.v1.schemas import UserSchema, NewUserSchema, DeviceSchema, NewDeviceSchema, DeviceSummarySchema, DeviceRequestQueryParamSchema
from app.v1.views.devices import Device as DeviceResource
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
class User(Resource):
	@marshal_with(UserSchema)
	def get(self, user_id: int):
		try:
			user = get_user(user_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return user

@api.route('/<int:user_id>/devices')
class UserDevices(Resource):
	@serialize_with(DeviceRequestQueryParamSchema, location=Location.QUERY_PARAMETER)
<<<<<<< HEAD
	@marshal_list_with(DeviceSummarySchema)
=======
	@marshal_list_with(DeviceSummary)
>>>>>>> master
	def get(self, user_id: int, query: dict):
		try:
			devices = get_devices(user_id, db.session, device_type=query['device_type'], device_state=query['device_state'])
		except Exception as e:
			raise InternalServerError

		return devices

	@serialize_with(NewDeviceSchema)
	def post(self, user_id: int, body: Device):
<<<<<<< HEAD
		try:
			device_id = create_device(user_id, body, db.session)
		except Exception as e:
			raise InternalServerError

		# TODO: return auth token for device
		return None, 201, {'Location': url_for('v1.devices_device', device_id=device_id)}
=======
		print(body)

		# body: dict | None = request.get_json()
		# if body is None:
		# 	raise BadRequest

		# try:
		# 	device = Device(
		# 		user_id = user_id,
		# 		model = body['model'],
		# 		device_type = body['device_type'],
		# 		device_state = DeviceStateEnum.Connecting.value,
		# 		name = body.get('name'),
		# 		api_version = body.get('api_version'),
		# 		software_version = body.get('software_version'),
		# 	)
		# 	# device_id = create_device()
		# except Exception as e:
		# 	pass
>>>>>>> master
