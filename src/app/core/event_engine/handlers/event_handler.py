from abc import ABC, abstractmethod
import itertools
from typing import Dict, List, Type
from app.common.schemas import DynamicField, SerializableClass
from app.core.event_engine.actions import Action
from app.core.event_engine.queries import Query
from app.core.event_engine.events import Event
from app.core.event_engine.triggers import Trigger
from sqlalchemy.orm.scoping import ScopedSession

from marshmallow import Schema, fields, EXCLUDE

import logging
logger = logging.getLogger(__name__)

#######################
# Schemas
#######################
class EventHandlerSchema(Schema):
	event_handler_id = fields.Int(dump_only=True)
	queries = fields.Dict(keys=fields.Str, values=DynamicField([Query]))
	triggers = fields.List(DynamicField([Trigger]))

	class Meta:
		# prevents issues loading event_handler_id
		exclude = ['event_handler_id']
#######################

class EventHandler(SerializableClass, ABC):
	__schema__ = EventHandlerSchema

	event_handler_id: int
	queries: Dict[str, Query]
	triggers: List[Trigger]
	supported_events: List[Type[Event]]

	def __init__(self, queries: Dict[str, Query], triggers: List[Trigger]) -> None:
		"""
		Args:
				query (Dict[str, Query]): Queries to retrieve data from
				triggers (List[Trigger]): Triggers to execute
		"""
		self.queries = queries
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

	def get_values(self, id: int, session: ScopedSession, event: Event):
		logging.info(f'Getting query values for event handler')
		values = {}
		for field, query in self.queries.items():
			values[field] = query.execute(id, session, event)

		logging.info(f'Values={values}')
		return values