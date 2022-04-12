from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import logging
from typing import Optional

from app.core.event_engine.events import Event
from app.common.schemas import SerializableClass

from marshmallow import Schema, fields

#######################
# Schemas
#######################
class ActionSchema(Schema):
	cooldown = fields.TimeDelta(required=False, allow_none=True)

	# DONT INCLUDE THESE FIELDS, they are stored in the database instead
	# action_id = fields.Int()
	# disabled = fields.Bool(required=True)
	# last_executed = fields.DateTime(required=False, allow_none=True)
#######################

# TODO: seperate action metadata from implementation for storage
class Action(SerializableClass, ABC):
	__schema__ = ActionSchema

	action_id: int | None
	disabled: bool
	cooldown: timedelta | None
	last_executed: datetime | None

	def __init__(self, disabled: bool, action_id: Optional[ int ] = None, cooldown: timedelta | None = None, last_executed: datetime | None = None):
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

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Action):
			return False

		return self.__dict__ == other.__dict__
		# return self.action_id == other.action_id and self.cooldown == other.cooldown and self.disabled == other.disabled