from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError
from app.core.services import get_device, edit_device, delete_device, record_data
from app.common.utils import marshal_with, serialize_with
from app.core.errors import NotFoundError
from app.core.models import Device, SensorData
from app.protocols.http.v1.schemas import DeviceSchema, DeviceUpdateSchema, SensorDataSchema

from flask_restx import Resource, Namespace
from app import db

from app.protocols.http.utils.authentication import deviceAuthenticator


api = Namespace('devices', description='Device related operations', path='/devices')

@api.route('/<int:device_id>')
class DeviceResource(Resource):
	@marshal_with(DeviceSchema)
	def get(self, device_id: int):
		try:
			device = get_device(device_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return device

	@serialize_with(DeviceUpdateSchema)
	def put(self, device_id: int, body: dict):
		try:
			edit_device(device_id, body, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 204

	def delete(self, device_id: int):
		try:
			delete_device(device_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 204

@api.route('/<int:device_id>/data')
class DeviceData(Resource):
	@serialize_with(SensorDataSchema)
	@deviceAuthenticator.login_required
	def post(self, device_id: int, body: SensorData):
		try:
			state = record_data(device_id, body, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		# TODO: return state update
		return None