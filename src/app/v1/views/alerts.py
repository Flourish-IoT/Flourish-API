from flask import current_app as app
from flask_restx import Resource, Namespace
from app.core.errors import NotFoundError, ConflictError
from app.core.services import delete_alert, set_viewed_state
from app.common.utils import marshal_with, serialize_with
from app.v1.schemas import AlertViewRequestSchema
from werkzeug.exceptions import NotFound, BadRequest, Conflict, InternalServerError
from app import db

api = Namespace('alerts', description='Alert related operations', path='/alerts')

@api.route('/<int:alert_id>')
class AlertResource(Resource):
	def delete(self, alert_id: int):
		try:
			delete_alert(alert_id, db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 204

@api.route('/view')
class AlertView(Resource):
	@serialize_with(AlertViewRequestSchema)
	def patch(self, body: dict):
		try:
			set_viewed_state(body['alert_ids'], body['viewed'], db.session)
		except NotFoundError as e:
			raise NotFound(str(e))
		except Exception as e:
			raise InternalServerError

		return None, 204