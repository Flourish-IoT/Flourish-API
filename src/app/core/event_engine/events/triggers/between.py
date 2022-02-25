import logging
from typing import Any, List, TypeVar, Generic

from app.core.event_engine.events import Event

from .actions import Action
from .trigger import Trigger
from app.core.util import Comparable

T = TypeVar('T', bound=Comparable)

class BetweenTrigger(Trigger, Generic[T]):
	min: T
	def __init__(self, min: T, max: T, actions: List[Action], *, field: str | None = None) -> None:
		super().__init__(actions, field)
		if min > max:
			raise ValueError('min must be less than max')

		self.min = min
		self.max = max

	def execute(self, v: T, event: Event) -> bool:
		logging.info('Executing equals trigger')
		value: T = self.get_value(v)

		if not (self.min < value and value < self.max):
			logging.info(f'{value} < {self.min} or {self.max} < {value}, not executing actions')
			return False

		logging.info(f'{self.min} < {value} < {self.max}, executing actions')
		self.execute_actions(event)

		return True