from datetime import datetime, timedelta
import logging
from app.core.event_engine.events import Event, DeviceEventType, PlantEventType
from app.core.event_engine.events.triggers.actions import Action
from app.core.models import SeverityLevelEnum, Alert
from app.core.services import create_alert


class GenerateAlertAction(Action):
	message_template: str
	severity: SeverityLevelEnum

	def __init__(self, message_template: str, severity: SeverityLevelEnum, disabled: bool, cooldown: timedelta | None = None):
		self.message_template = message_template
		self.severity = severity
		super().__init__(disabled, cooldown)

	def generate_message(self, event: Event) -> str:
		# do we need to clean data first? Could leak user info if we have user events
		return self.message_template.format(event=event)

	def execute(self, event: Event) -> bool:
		logging.info('Executing GenerateAlertAction')
		if not self.can_execute():
			return False

		message = self.generate_message(event)
		logging.info(f'Persisting alert: message={message}, severity={self.severity}')

		alert = Alert(message=message, severity=self.severity, time=datetime.now())
		match event:
			case PlantEventType(plant):
				alert.plant_id = plant.plant_id
			case DeviceEventType(device):
				alert.device_id = device.device_id
			case _:
				logging.error(f'Unsupported event type: {event}')
				raise ValueError(f'Unsupported event type: {event}')

		# persist alert
		create_alert(event.user_id, alert, event.session)

		# TODO: push notification
		return True