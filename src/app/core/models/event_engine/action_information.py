from __future__ import annotations
from datetime import datetime
import json
import logging
from typing import cast

from app.core.event_engine.actions import Action
from app.common.schemas import DynamicSchema
from ..base_model import BaseModel
from sqlalchemy import Column, Integer, TIMESTAMP, Boolean, ForeignKey, Identity, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type
from marshmallow import INCLUDE

# rename to ActionMetadata and create new class ActionDefinition to store actual action
class ActionInformation(BaseModel):
	__tablename__ = 'actions'

	action_id = cast(int | None, Column(
		Integer,
		Identity(True),
		primary_key = True
	))

	event_handler_id = cast(int, Column(
		Integer,
		ForeignKey('event_handlers.event_handler_id', ondelete='CASCADE'),
	))

	disabled = cast(bool, Column(
		Boolean,
		server_default=text('FALSE'),
		nullable=False
	))

	last_executed = cast(datetime | None, Column(
		TIMESTAMP(True)
	))

	action = cast(dict, Column(
		mutable_json_type(dbtype=JSONB, nested=True),
		nullable=False
	))

	_action: Action

	def to_action(self) -> Action:
		try:
			action = DynamicSchema().load({
				**{
					'action_id': self.action_id,
					'disabled': self.disabled,
					'last_executed': self.last_executed
				},
				**self.action
			},
			# HACK: nested meta classes are currently ignored and will fail to deserialize if this is not specified at load level https://github.com/marshmallow-code/marshmallow/issues/1490
			unknown=INCLUDE)
		except Exception as e:
			logging.error(f"Failed to load action")
			logging.exception(e)
			raise e

		if not isinstance(action, Action):
			raise ValueError("Failed to decode action: ", action)

		self._action = action
		return action

	@staticmethod
	def from_action(action: Action):
		action_json = DynamicSchema().dump(action)
		action_info = ActionInformation(action_id=action.action_id, last_executed=action.last_executed, disabled=action.disabled, action=action_json)
		# use this to tie together the action information with the action that created it. Useful when initially creating the action and backfilling the IDs
		action_info._action = action
		return action_info