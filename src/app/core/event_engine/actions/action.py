from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import logging

from app.core.event_engine.events import Event
from app.common.utils import Serializable

from marshmallow import Schema, fields

#######################
# Schemas
#######################
class ActionSchema(Schema):
	action_id = fields.Int()
	disabled = fields.Bool(required=True)
	cooldown = fields.TimeDelta(required=True, allow_none=True)
	last_executed = fields.DateTime(required=True, allow_none=True)
#######################

class Action(Serializable, ABC):
	__schema__ = ActionSchema

	action_id: int | None
	disabled: bool
	cooldown: timedelta | None
	last_executed: datetime | None

	def __init__(self, disabled: bool, action_id: int | None = None, cooldown: timedelta | None = None, last_executed: datetime | None = None):
		"""
		Args:
				disabled (bool): Enables/disables action
				cooldown (timedelta | None, optional): Action cooldown. Defaults to None.
		"""
		self.action_id = action_id
		self.disabled = disabled
		self.cooldown = cooldown
		self.last_executed = last_executed

	def can_execute(self) -> bool:
		"""Determines if action can execute based on whether or not is has been disabled or is on cooldown

		Returns:
				bool: Action can execute
		"""
		logging.info('Checking if action can execute')
		if self.disabled:
			logging.info('Action disabled, not executing')
			return False

		if self.cooldown is not None:
			logging.info(f'Cooldown is {self.cooldown}, checking if action still on cooldown')
			# TODO: check if on cooldown

		logging.info('Action can execute')
		return True

	def update_last_executed(self):
		# TODO
		pass

	@abstractmethod
	def execute(self, event: Event) -> bool:
		"""Executes action

		Args:
				event (Event): Event information

		Returns:
				bool: Action executed
		"""
		pass