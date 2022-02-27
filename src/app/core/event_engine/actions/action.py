from abc import ABC, abstractmethod
from datetime import timedelta
import logging

from app.core.event_engine.events import Event

class Action(ABC):
	disabled: bool
	cooldown: timedelta | None

	def __init__(self, disabled: bool, cooldown: timedelta | None = None):
		"""
		Args:
				disabled (bool): Enables/disables action
				cooldown (timedelta | None, optional): Action cooldown. Defaults to None.
		"""
		self.disabled = disabled
		self.cooldown = cooldown

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

	@abstractmethod
	def execute(self, event: Event) -> bool:
		"""Executes action

		Args:
				event (Event): Event information

		Returns:
				bool: Action executed
		"""
		pass