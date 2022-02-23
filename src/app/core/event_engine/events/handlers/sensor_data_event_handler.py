from typing import List
from app.core.event_engine.events.field import Field
from app.core.event_engine.events.handlers import EventHandler
from app.core.event_engine.events import SensorDataEvent
from sqlalchemy.orm.scoping import ScopedSession

from app.core.event_engine.events.triggers import Trigger

class SensorDataEventHandler(EventHandler):
	def __init__(self, field: Field, triggers: List[Trigger]) -> None:
			super().__init__(field, triggers, [SensorDataEvent])

	def handle(self, event: SensorDataEvent, session: ScopedSession):
		if not self.can_handle(event):
			return

		# get field value
		value = self.field.get_value(event.plant, session)

		# execute triggers
		for trigger in self.triggers:
			trigger.execute(value)