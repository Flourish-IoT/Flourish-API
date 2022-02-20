import logging
from typing import Any, TypeVar, Generic
from .trigger import Trigger
from app.core.util import Comparable

T = TypeVar('T', bound=Comparable)

class BetweenTrigger(Trigger, Generic[T]):
	min: T
	def __init__(self, actions: list, min: T, max: T) -> None:
		super().__init__(actions)
		if min > max:
			raise ValueError('min must be less than max')

		self.min = min
		self.max = max

	def execute(self, value: T):
		logging.info('Executing equals trigger')

		if not (self.min < value and value < self.max):
			logging.info(f'{value} < {self.min} or {self.max} < {value}, not executing actions')
			return False

		logging.info(f'{self.min} < {value} < {self.max}, executing actions')
		self._execute_actions()

		return True