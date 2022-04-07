from datetime import datetime
import logging
from typing import Dict, cast
from app.common.utils.polymorphic_schema import PolymorphicSchema

import app.core.event_engine.actions as actions
import app.core.event_engine.handlers as handlers
# from app.core.services.event_handler_service import get_event_handler_actions

from ..base_model import BaseModel
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type
from sqlalchemy.orm.scoping import ScopedSession

class EventHandlerInformation(BaseModel):
	__tablename__ = 'event_handlers'

	event_handler_id = cast(int, Column(
		Integer,
		primary_key = True
	))

	plant_id = cast(int | None, Column(
		Integer,
		ForeignKey('plants.plant_id'),
	))

	device_id = cast(int | None, Column(
		Integer,
		ForeignKey('devices.device_id'),
	))

	config = Column(
		mutable_json_type(dbtype=JSONB, nested=True),
		nullable=False
	)

	# def to_event_handler(self, session: ScopedSession):
	# 	actions = get_event_handler_actions(self.event_handler_id, session)
	# 	action_map = {action.action_id: action.to_action() for action in actions}

	# 	schema = PolymorphicSchema()
	# 	schema.context = {'action_map': action_map}
	# 	try:
	# 		event_handler = PolymorphicSchema().load(self.config)
	# 	except Exception as e:
	# 		logging.error(f"Failed to load event handler")
	# 		logging.exception(e)
	# 		raise e

	# 	if not isinstance(event_handler, handlers.EventHandler):
	# 		raise ValueError("Failed to decode event handler: ", event_handler)

	# 	return event_handler

	@staticmethod
	def from_event_handler(event_handler: handlers.EventHandler):
		event_handler_information = EventHandlerInformation()
		# event_handler_information = EventHandlerInformation(event_handler_id=event_handler.)
		config = PolymorphicSchema().dump(event_handler)
		event_handler_information.config = config
		return event_handler_information