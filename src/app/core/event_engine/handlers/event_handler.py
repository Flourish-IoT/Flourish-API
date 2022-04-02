from abc import ABC, abstractmethod
import itertools
from typing import List, Type
import app.core.event_engine.triggers as event_triggers
import app.core.event_engine.events as events
import app.core.event_engine.actions as actions
import app.core.event_engine as event_engine
# from app.core.event_engine import Field
# from app.core.event_engine.actions import Action
# from app.core.event_engine.events import Event
# from app.core.event_engine.triggers import Trigger

class EventHandler(ABC):
	# event_handler_id: int
	field: event_engine.Field
	triggers: List[event_triggers.Trigger]
	supported_events: List[Type[events.Event]]

	def __init__(self, field: event_engine.Field, triggers: List[event_triggers.Trigger]) -> None:
		"""
		Args:
				field (Field): Field used for retrieving data
				triggers (List[Trigger]): Triggers to execute
		"""
		self.field = field
		self.triggers = triggers

	def can_handle(self, event: events.Event) -> bool:
		"""Determines if EventHandler can handle an event

		Args:
				event (Event): Event being tested

		Returns:
				bool: Indicates whether or not EventHandler can handle event
		"""
		return type(event) in self.supported_events

	def get_actions(self) -> List[actions.Action]:
		# get actions from triggers and flatten it
		return list(itertools.chain.from_iterable([trigger.get_actions() for trigger in self.triggers]))

	@abstractmethod
	def handle(self, event: events.Event):
		"""Handles an event. Retrieves Field value and executes all triggers

		Args:
				event (Event): Event being handled
		"""
		raise NotImplementedError
