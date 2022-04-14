from functools import reduce
import itertools
import logging
from typing import List, TypeVar, Generic
from app.common.schemas import DynamicField
from app.core.util import Comparable
from app.core.event_engine.events import Event
from app.core.event_engine.triggers import Trigger, TriggerSchema
from app.core.event_engine.actions import Action

from marshmallow import post_load, fields

#######################
# Schemas
#######################
class AndTriggerSchema(TriggerSchema):
	triggers = fields.List(DynamicField([Trigger]))

	class Meta():
		exclude = ['field']

	@post_load
	def make(self, data, **kwargs):
		return AndTrigger(**data)
#######################

T = TypeVar('T', bound=Comparable)
class AndTrigger(Trigger, Generic[T]):
	"""Executes if all nested triggers return True"""
	__schema__ = AndTriggerSchema

	def __init__(self, triggers: List[Trigger[T]], actions: List[Action] = []) -> None:
		"""
		Args:
				triggers (List[Trigger[T]]): Triggers to test
				actions (List[Action], optional): Actions to execute on success. Defaults to [].
		"""
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

	def get_actions(self) -> List[Action]:
		# get actions from sub triggers and flatten it
		return [*self.actions, *itertools.chain.from_iterable([trigger.get_actions() for trigger in self.triggers]) ]