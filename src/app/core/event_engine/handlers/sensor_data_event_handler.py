from typing import List, cast
from app.core.event_engine import Field
from app.core.event_engine.handlers import EventHandler
from app.core.event_engine.events import SensorDataEvent, Event

from app.core.event_engine.triggers import Trigger

class SensorDataEventHandler(EventHandler):
	"""An EventHandler to handle SensorDataEvents"""
	events = [SensorDataEvent]
	def __init__(self, field: Field, triggers: List[Trigger]) -> None:
		super().__init__(field, triggers)

	def handle(self, event: Event):
		if not self.can_handle(event):
			return

		# type hack. self.can_handle doesn't narrow down type, so we need to do it explicitly
		event = cast(SensorDataEvent, event)

		# get field value
		value = self.field.get_value(event.plant.plant_id, event.session)

		# execute triggers
		for trigger in self.triggers:
			trigger.execute(value, event)