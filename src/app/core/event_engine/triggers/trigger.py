from abc import ABC, abstractmethod
import logging
from typing import Any, List, TypeVar, Generic
from app.core.event_engine.events import Event
from app.core.event_engine.actions import Action

T = TypeVar('T')

class Trigger(ABC, Generic[T]):
	actions: List[Action]
	field: str | None

	def __init__(self, actions: List[Action], field: str | None = None) -> None:
		"""
		Args:
				actions (List[Action]): List of actions to execute if the trigger executes
				field (str | None, optional): Field to use when testing trigger value. Defaults to None.
		"""
		self.actions = actions
		self.field = field

	@abstractmethod
	def execute(self, value: T, event: Event) -> bool:
		"""Tests trigger condition and executes actions on success

		Args:
				value (T): Value to test
				event (Event): Event information

		Returns:
				bool: Executed succesfully
		"""
		raise NotImplementedError

	def get_value(self, value: T) -> T:
		"""Retrieves a value from the value being tested using the field

		Args:
				value (T)

		Returns:
				T: value
		"""
		logging.info('Getting value')
		# for nested fields
		if self.field is not None:
			logging.info(f'Using field {self.field}')
			# TODO: better error handling here if field does not exist
			# if self.field in value:
			# 	pass
			if isinstance(value, dict):
				value = value[self.field]

		logging.info(f'Value is {value}')

		return value

	def execute_actions(self, event: Event):
		"""Executes trigger actions

		Args:
				event (Event): Event information
		"""
		for action in self.actions:
			action.execute(event)

	def get_actions(self) -> List[Action]:
		return self.actions