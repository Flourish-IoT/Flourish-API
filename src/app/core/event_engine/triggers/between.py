import logging
from typing import Any, List, TypeVar, Generic
from . import Trigger
from app.core.event_engine.events import Event
from app.core.event_engine.actions import Action
from app.core.event_engine.triggers import Trigger, TriggerSchema
from app.common.schemas import DynamicField
from app.core.util import Comparable

from marshmallow import post_load

#######################
# Schemas
#######################
class BetweenTriggerSchema(TriggerSchema):
	min = DynamicField()
	max = DynamicField()

	@post_load
	def make(self, data, **kwargs):
		return BetweenTrigger(**data)
#######################

T = TypeVar('T', bound=Comparable)
class BetweenTrigger(Trigger, Generic[T]):
	"""Executes actions if value is between defined values"""
	__schema__ = BetweenTriggerSchema

	min: T
	max: T

	def __init__(self, min: T, max: T, actions: List[Action], *, field: str | None = None) -> None:
		"""
		Args:
				min (T): Minimum value
				max (T): Maximum value
				actions (List[Action]): Actions to execute on success
				field (str | None, optional): Field to use when testing trigger value. Defaults to None.

		Raises:
				ValueError: Minimum value is less than maximum
		"""
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