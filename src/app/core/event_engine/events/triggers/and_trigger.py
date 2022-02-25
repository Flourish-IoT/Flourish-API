import logging
from typing import List, TypeVar, Generic
from app.core.event_engine.events import Event

from app.core.util import Comparable
from .trigger import Trigger
from .actions import Action

T = TypeVar('T', bound=Comparable)

class AndTrigger(Trigger, Generic[T]):
	def __init__(self, triggers: List[Trigger[T]], actions: List[Action] = []) -> None:
		super().__init__(actions)
		self.triggers = triggers

	def execute(self, value: T, event: Event) -> bool:
		logging.info('Executing and trigger')

		if not all([trigger.execute(value, event) for trigger in self.triggers]):
			logging.info(f'{value} did not pass all nested triggers, not executing actions')
			return False

		logging.info(f'{value} passed all nested triggers, executing actions')
		self.execute_actions(event)

		return True
