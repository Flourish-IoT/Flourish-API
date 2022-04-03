from abc import ABC, abstractmethod
import itertools
from typing import List, Type
from app.common.utils.polymorphic_schema import PolymorphicSchema
from app.core.event_engine import Field
from app.core.event_engine.actions import Action
from app.core.event_engine.events import Event
from app.core.event_engine.triggers import Trigger
from marshmallow import Schema, fields

#######################
# Schemas
#######################
class EventHandlerSchema(Schema):
	event_handler_id = fields.Int()
	field = fields.Nested(PolymorphicSchema)
	triggers = fields.Nested(PolymorphicSchema, many=True)
#######################


class EventHandler(ABC):
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
