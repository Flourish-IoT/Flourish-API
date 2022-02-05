from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError
from app.core.services import get_devices, get_device
from app.common.utils.marshal import marshal_with
from app.core.errors import NotFoundError
from app.v1.schemas import DeviceSchema

from flask_restx import Resource, Namespace
from app import db


api = Namespace('devices', description='Device related operations', path='/devices')

@api.route('/<int:device_id>')
class Device(Resource):
	@marshal_with(DeviceSchema)
	def get(self, device_id: int):
		# TODO: authentication
		try:
			device = get_device(device_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return device