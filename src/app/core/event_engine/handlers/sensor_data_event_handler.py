from typing import Dict, List, cast
from app.core.event_engine.handlers import EventHandler, EventHandlerSchema
from app.core.event_engine.events import SensorDataEvent, Event
from app.core.event_engine.queries import Query
from app.core.event_engine.triggers import Trigger
from marshmallow import post_load

class SensorDataEventHandlerSchema(EventHandlerSchema):
	@post_load
	def make(self, data, **kwargs):
		return SensorDataEventHandler(**data)

class SensorDataEventHandler(EventHandler):
	"""An EventHandler to handle SensorDataEvents"""
	__schema__ = SensorDataEventHandlerSchema

	supported_events = [SensorDataEvent]
	def __init__(self, queries: Dict[str, Query], triggers: List[Trigger]) -> None:
		super().__init__(queries, triggers)

	def handle(self, event: Event):
		if not self.can_handle(event):
			return

		# type hack. self.can_handle doesn't narrow down type, so we need to do it explicitly
		event = cast(SensorDataEvent, event)

		# get field value
		value = self.get_values(event.plant.plant_id, event.session, event)

		# execute triggers
		for trigger in self.triggers:
			trigger.execute(value, event)