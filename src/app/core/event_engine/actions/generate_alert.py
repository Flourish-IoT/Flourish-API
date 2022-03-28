from datetime import datetime, timedelta
import logging
from app.core.event_engine.actions.action import ActionSchema
from app.core.event_engine.events import Event, DeviceEventType, PlantEventType
from app.core.event_engine.actions import Action
from app.core.models import SeverityLevelEnum, Alert
from app.core.services import create_alert

from marshmallow import fields, validate, post_load, validates_schema, ValidationError
from marshmallow_enum import EnumField
from app.core.models import SeverityLevelEnum
from app.common.utils import PolymorphicSchema

#######################
# Schemas
#######################
class GenerateAlertActionSchema(ActionSchema):
	message_template = fields.Str()
	severity = EnumField(SeverityLevelEnum)

	@post_load
	def make(self, data, **kwargs):
		return GenerateAlertAction(**data)

class GenerateDeviceAlertActionSchema(GenerateAlertActionSchema):
	pass

class GeneratePlantAlertActionSchema(GenerateAlertActionSchema):
	pass
#######################

class GenerateAlertAction(Action):
	__schema__ = GenerateAlertActionSchema

	message_template: str
	severity: SeverityLevelEnum
	# TODO:
	# push_notification: bool

	def __init__(self, message_template: str, severity: SeverityLevelEnum, disabled: bool, action_id: int | None, cooldown: timedelta | None = None, last_executed: datetime | None = None):
		"""Generates an alert

		Args:
				message_template (str): A template string used to create the alert message. Event information is available for templating
				severity (SeverityLevelEnum): Severity of alert
				disabled (bool): Enables/disables action
				cooldown (timedelta | None, optional): Action cooldown. Defaults to None.
		"""
		# TODO: message template should come from db eventually
		self.message_template = message_template
		self.severity = severity
		super().__init__(disabled, action_id=action_id, cooldown=cooldown, last_executed=last_executed)

	def generate_message(self, event: Event) -> str:
		"""Generates alert message

		Args:
				event (Event): Event to use for templating

		Returns:
				str: Generated message
		"""
		# do we need to clean data first? Could leak user info if we have user events
		return self.message_template.format(event=event)

	def generate(self, event: Event) -> Alert:
		"""Generates an Alert object

		Args:
				event (Event): Event used to generate alert

		Returns:
				Alert: Generated Alert object
		"""
		message = self.generate_message(event)
		alert = Alert(message=message, severity=self.severity, time=datetime.now())
		return alert

	def execute(self, event: Event) -> bool:
		"""Executes action. Generates an Alert object and persists it in the database

		Args:
				event (Event): Event used to generate Alert

		Returns:
				bool: Whether or not action executed succesfully
		"""
		logging.info('Executing GenerateAlertAction')
		if not self.can_execute():
			return False

		alert = self.generate(event)
		logging.info(f'Persisting alert: {alert}')

		# persist alert
		create_alert(event.user_id, alert, event.session)

		# TODO: push notification
		return True

class GeneratePlantAlertAction(GenerateAlertAction):
	__schema__ = GeneratePlantAlertActionSchema

	def generate(self, event: PlantEventType):
		alert = super().generate(event)
		alert.plant_id = event.plant.plant_id
		return alert

class GenerateDeviceAlertAction(GenerateAlertAction):
	__schema__ = GenerateDeviceAlertActionSchema

	def generate(self, event: DeviceEventType):
		alert = super().generate(event)
		alert.device_id = event.device.device_id
		return alert