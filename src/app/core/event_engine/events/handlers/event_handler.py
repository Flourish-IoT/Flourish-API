from abc import ABC, abstractmethod
from typing import List
from app.core.event_engine.events import Event

from app.core.event_engine.events.field import Field
from app.core.event_engine.events.triggers import Trigger

class EventHandler(ABC):
	field: Field
	triggers: List[Trigger]
	def __init__(self, field: Field, triggers: List[Trigger]) -> None:
		self.field = field
		self.triggers = triggers

	@abstractmethod
	def handle(self, event: Event):
		raise NotImplementedError
