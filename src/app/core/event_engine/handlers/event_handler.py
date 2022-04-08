from abc import ABC, abstractmethod
import itertools
from typing import List, Type
from app.common.utils import PolymorphicSchema
from app.common.schemas import DynamicField, SerializableClass
from app.core.event_engine import Field, FieldSchema
from app.core.event_engine.actions import Action
from app.core.event_engine.events import Event
from app.core.event_engine.triggers import Trigger, TriggerSchema

from marshmallow import Schema, fields

#######################
# Schemas
#######################
class EventHandlerSchema(Schema):
	event_handler_id = fields.Int()
	field = DynamicField([Field])
	triggers = fields.List(DynamicField([Trigger]))
#######################

class EventHandler(SerializableClass, ABC):
	__schema__ = EventHandlerSchema

	event_handler_id: int
	field: Field
	triggers: List[Trigger]
	supported_events: List[Type[Event]]

	def __init__(self, field: Field, triggers: List[Trigger]) -> None:
		"""
		Args:
				field (Field): Field used for retrieving data
				triggers (List[Trigger]): Triggers to execute
		"""
		self.field = field
		self.triggers = triggers

	def can_handle(self, event: Event) -> bool:
		"""Determines if EventHandler can handle an event

		Args:
				event (Event): Event being tested

		Returns:
				bool: Indicates whether or not EventHandler can handle event
		"""
		return type(event) in self.supported_events

	def get_actions(self) -> List[Action]:
		# get actions from triggers and flatten it
		return list(itertools.chain.from_iterable([trigger.get_actions() for trigger in self.triggers]))

	@abstractmethod
	# TODO: add new param for info to be returned to device
	def handle(self, event: Event):
		"""Handles an event. Retrieves Field value and executes all triggers

		Args:
				event (Event): Event being handled
		"""
		raise NotImplementedError

	def dump(self):
		actions = self.get_actions()