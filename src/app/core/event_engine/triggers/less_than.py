import logging
from typing import List, TypeVar, Generic
from app.core.util import Comparable
from . import Trigger
from app.core.event_engine.events import Event
from app.core.event_engine.triggers import Trigger
from app.core.event_engine.actions import Action

T = TypeVar('T', bound=Comparable)

class LessThanTrigger(Trigger, Generic[T]):
	"""Executes if value is less than trigger value"""
	def __init__(self, value: T, actions: List[Action] = [], *, field: str | None = None) -> None:
		"""
		Args:
				value (T): Value to test against
				actions (List[Action], optional): Actions to execute on success. Defaults to [].
				field (str | None, optional): Field to use when testing trigger value. Defaults to None.
		"""
		super().__init__(actions, field)
		self.value = value

	def execute(self, v: T | dict, event: Event) -> bool:
		logging.info('Executing less than trigger')
		value: T = self.get_value(v)

		if not value < self.value:
			logging.info(f'{value} > {self.value}, not executing actions')
			return False

		logging.info(f'{value} < {self.value}, executing actions')
		self.execute_actions(event)

		return True