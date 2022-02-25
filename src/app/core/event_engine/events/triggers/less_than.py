import logging
from typing import List, TypeVar, Generic
from app.core.event_engine.events import Event

from app.core.util import Comparable
from .trigger import Trigger
from .actions import Action

T = TypeVar('T', bound=Comparable)

class LessThanTrigger(Trigger, Generic[T]):
	def __init__(self, value: T, actions: List[Action] = [], *, field: str | None = None) -> None:
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