from app.core.event_engine.events.handlers import EventHandler
from app.core.event_engine.events import SensorDataEvent
from sqlalchemy.orm.scoping import ScopedSession

class SensorDataEventHandler(EventHandler):
	def handle(self, event: SensorDataEvent, session: ScopedSession):
		# get field value
		value = self.field.get_value(event.plant_id, session)

		# execute triggers
		for trigger in self.triggers:
			trigger.execute(value)