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
		self.field = field
		self.triggers = triggers

	def can_handle(self, event: Event):
		return type(event) in self.events

	@abstractmethod
	def handle(self, event: Event):
		raise NotImplementedError
