from abc import ABC, abstractmethod
from typing import List, Type
from app.core.event_engine import Field
from app.core.event_engine.events import Event
from app.core.event_engine.triggers import Trigger

class EventHandler(ABC):
	field: Field
	triggers: List[Trigger]
	events: List[Type[Event]]

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
		return type(event) in self.events

	@abstractmethod
	def handle(self, event: Event):
		"""Handles an event. Retrieves Field value and executes all triggers

		Args:
				event (Event): Event being handled
		"""
		raise NotImplementedError
