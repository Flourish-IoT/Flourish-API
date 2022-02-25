from typing import List
from app.core.event_engine import Field
from app.core.event_engine.handlers import EventHandler
from app.core.event_engine.events import SensorDataEvent
from sqlalchemy.orm.scoping import ScopedSession

from app.core.event_engine.triggers import Trigger

class SensorDataEventHandler(EventHandler):
	events = [SensorDataEvent]
	def __init__(self, field: Field, triggers: List[Trigger]) -> None:
		super().__init__(field, triggers)

	def handle(self, event: SensorDataEvent, session: ScopedSession):
		if not self.can_handle(event):
			return

		# get field value
		value = self.field.get_value(event.plant.plant_id, session)

		# execute triggers
		for trigger in self.triggers:
			trigger.execute(value, event)