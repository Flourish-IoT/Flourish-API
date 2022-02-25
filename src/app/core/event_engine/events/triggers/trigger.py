from abc import ABC, abstractmethod
import logging
from typing import Any, List, TypeVar, Generic

from app.core.event_engine.events import Event
from .actions import Action

T = TypeVar('T')

class Trigger(ABC, Generic[T]):
	actions: List[Action]
	field: str | None

	def __init__(self, actions: List[Action], field: str | None = None) -> None:
		self.actions = actions
		self.field = field

	@abstractmethod
	def execute(self, value: T, event: Event) -> bool:
		raise NotImplementedError

	def get_value(self, value: T) -> T:
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
		for action in self.actions:
			action.execute(event)