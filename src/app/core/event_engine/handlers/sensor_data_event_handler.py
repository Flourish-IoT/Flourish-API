from typing import List, cast
import app.core.event_engine.events as engine_events
import app.core.event_engine.handlers as handlers
import app.core.event_engine.triggers as triggers
import app.core.event_engine as event_engine
# from app.core.event_engine import Field
# from app.core.event_engine.handlers import EventHandler
# from app.core.event_engine.events import SensorDataEvent, Event
# from app.core.event_engine.triggers import Trigger

class SensorDataEventHandler(handlers.EventHandler):
	"""An EventHandler to handle SensorDataEvents"""
	events = [engine_events.SensorDataEvent]
	def __init__(self, field: event_engine.Field, triggers: List[triggers.Trigger]) -> None:
		super().__init__(field, triggers)

	def handle(self, event: engine_events.Event):
		if not self.can_handle(event):
			return

		# type hack. self.can_handle doesn't narrow down type, so we need to do it explicitly
		event = cast(engine_events.SensorDataEvent, event)

		# get field value
		value = self.field.get_value(event.plant.plant_id, event.session)

		# execute triggers
		for trigger in self.triggers:
			trigger.execute(value, event)