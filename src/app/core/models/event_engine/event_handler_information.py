from datetime import datetime
import logging
from typing import Dict, List, cast
from app.common.schemas import DynamicSchema

import app.core.event_engine.actions as actions
import app.core.event_engine.handlers as handlers
from app.core.models.event_engine.action_information import ActionInformation

from ..base_model import BaseModel
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type
from sqlalchemy.orm import relationship

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

	action_information = cast(List[ActionInformation] | None , relationship("ActionInformation", cascade='all, delete-orphan') )

	def to_event_handler(self, action_map: Dict[int | None, actions.Action]):
		try:
			event_handler = DynamicSchema(context={'action_map': action_map}).load(self.config)
		except Exception as e:
			logging.error(f"Failed to load event handler")
			logging.exception(e)
			raise e

		if not isinstance(event_handler, handlers.EventHandler):
			raise ValueError("Failed to decode event handler: ", event_handler)

		return event_handler

	def update_config(self, event_handler: handlers.EventHandler):
		config = DynamicSchema().dump(event_handler)
		self.config = config