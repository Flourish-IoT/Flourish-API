from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError
from app.core.services import get_devices

from flask_restx import Resource, Namespace
from app import db


api = Namespace('devices', description='Device related operations', path='/devices')

@api.route('/<int:device_id>')
class Device(Resource):
	def get(self, device_id: int):
		# TODO: authentication


		return device_id