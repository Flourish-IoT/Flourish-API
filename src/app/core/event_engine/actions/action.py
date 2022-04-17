from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from app.core.event_engine.events import Event
from app.common.schemas import SerializableClass
import app.core.services.event_handler_service as services

from marshmallow import Schema, fields, INCLUDE

import logging
logger = logging.getLogger(__name__)

#######################
# Schemas
#######################
class ActionSchema(Schema):
	cooldown = fields.TimeDelta(required=False, allow_none=True)

	class Meta:
		unknown = INCLUDE

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
	last_executed: datetime | None

	cooldown: timedelta | None

	# information: models.

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
		logger.info('Checking if action can execute')
		if self.disabled:
			logger.info('Action disabled, not executing')
			return False

		if self.cooldown is not None:
			logger.info(f'Cooldown is {self.cooldown}, last executed {self.last_executed}, checking if action still on cooldown')
			# if the action has been executed before, and the time between when it was last ran is longer than the cooldown, action can run
			return self.last_executed is None or datetime.now() - self.last_executed > self.cooldown

		logger.info('Action can execute')
		return True

	def update_last_executed(self, event: Event):
		self.last_executed = datetime.now()
		if self.action_id is not None:
			services.update_action_last_executed(self.action_id, self.last_executed, event.session)

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