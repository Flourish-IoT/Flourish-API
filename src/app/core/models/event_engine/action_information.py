from datetime import datetime
import json
import logging
from typing import cast

from app.core.event_engine.actions import Action
from app.common.utils import PolymorphicSchemaLoader
from ..base_model import BaseModel
from sqlalchemy import Column, Integer, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type

class ActionInformation(BaseModel):
	__tablename__ = 'actions'

	action_id = cast(int, Column(
		Integer,
		primary_key = True
	))

	event_handler_id = cast(int, Column(
		Integer,
		ForeignKey('event_handlers.event_handler_id'),
	))

	action = cast(dict, Column(
		mutable_json_type(dbtype=JSONB, nested=True),
		nullable=False
	))

	def to_action(self) -> Action:
		try:
			action = PolymorphicSchemaLoader().load(self.action)
		except Exception as e:
			logging.error(f"Failed to load action")
			logging.exception(e)
			raise e

		if not isinstance(action, Action):
			raise ValueError("Failed to decode action: ", action)

		return action

	@staticmethod
	def from_action(action: Action):
		a = ActionInformation(action_id=action.action_id)
		action_json = action.marshal()
		a.action = action_json
		return a