from functools import reduce
import itertools
import logging
from typing import List, TypeVar, Generic
from app.core.util import Comparable
import app.core.event_engine.events as events
from . import Trigger
import app.core.event_engine.actions as actions
# from app.core.event_engine.events import Event
# from app.core.event_engine.triggers import Trigger
# from app.core.event_engine.actions import Action

T = TypeVar('T', bound=Comparable)

class AndTrigger(Trigger, Generic[T]):
	"""Executes if all nested triggers return True"""
	def __init__(self, triggers: List[Trigger[T]], actions: List[actions.Action] = []) -> None:
		"""
		Args:
				triggers (List[Trigger[T]]): Triggers to test
				actions (List[Action], optional): Actions to execute on success. Defaults to [].
		"""
		super().__init__(actions)
		self.triggers = triggers

	def execute(self, value: T, event: events.Event) -> bool:
		logging.info('Executing and trigger')

		if not all([trigger.execute(value, event) for trigger in self.triggers]):
			logging.info(f'{value} did not pass all nested triggers, not executing actions')
			return False

		logging.info(f'{value} passed all nested triggers, executing actions')
		self.execute_actions(event)

		return True

	def get_actions(self) -> List[actions.Action]:
		# get actions from sub triggers and flatten it
		return list(itertools.chain.from_iterable([trigger.get_actions() for trigger in self.triggers]))