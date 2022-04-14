from datetime import datetime
import json
import logging
from typing import cast

import app.core.event_engine.actions as actions
from app.common.schemas import DynamicSchema
from ..base_model import BaseModel
from sqlalchemy import Column, Integer, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type

# rename to ActionMetadata and create new class ActionDefinition to store actual action
class ActionInformation(BaseModel):
	__tablename__ = 'actions'

	action_id = cast(int | None, Column(
		Integer,
		primary_key = True
	))

	event_handler_id = cast(int, Column(
		Integer,
		ForeignKey('event_handlers.event_handler_id'),
	))

	disabled = cast(bool, Column(
		Boolean
	))

	last_executed = cast(datetime | None, Column(
		TIMESTAMP
	))

	action = cast(dict, Column(
		mutable_json_type(dbtype=JSONB, nested=True),
		nullable=False
	))

	_action: actions.Action

	def to_action(self) -> actions.Action:
		try:
			action = DynamicSchema(context={
				'action_id': self.action_id,
				'disabled': self.disabled,
				'last_executed': self.last_executed
			}).load(self.action)
		except Exception as e:
			logging.error(f"Failed to load action")
			logging.exception(e)
			raise e

		if not isinstance(action, actions.Action):
			raise ValueError("Failed to decode action: ", action)

		self._action = action
		return action

	@staticmethod
	def from_action(action: actions.Action):
		action_json = DynamicSchema().dump(action)
		action_info = ActionInformation(action_id=action.action_id, last_executed=action.last_executed, disabled=action.disabled, action=action_json)
		# use this to tie together the action information with the action that created it. Useful when initially creating the action and backfilling the IDs
		action_info._action = action
		return action_info