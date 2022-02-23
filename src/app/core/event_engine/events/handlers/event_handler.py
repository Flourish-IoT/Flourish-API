from abc import ABC, abstractmethod
from typing import List
from app.core.event_engine.events import Event

from app.core.event_engine.events.field import Field
from app.core.event_engine.events.triggers import Trigger

class EventHandler(ABC):
	field: Field
	triggers: List[Trigger]
	events: List[Event]

	def __init__(self, field: Field, triggers: List[Trigger], events: List[Event]) -> None:
		self.field = field
		self.triggers = triggers
		self.events = events

	def can_handle(self, event: Event):
		return type(event) in self.events

	@abstractmethod
	def handle(self, event: Event):
		raise NotImplementedError
