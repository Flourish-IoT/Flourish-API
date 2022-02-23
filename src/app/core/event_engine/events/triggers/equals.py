
import logging
from typing import List, TypeVar, Generic

from app.core.util import Comparable
from .trigger import Trigger
from .actions import Action

T = TypeVar('T', bound=Comparable)

class EqualsTrigger(Trigger, Generic[T]):
	def __init__(self, value: T, actions: List[Action]) -> None:
		super().__init__(actions)
		self.value = value

	def execute(self, value: T) -> bool:
		logging.info('Executing equals trigger')
		if self.value != value:
			logging.info(f'{self.value} != {value}, not executing actions')
			return False

		logging.info(f'{self.value} == {value}, executing actions')
		self._execute_actions()

		return True