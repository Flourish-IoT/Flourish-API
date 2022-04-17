from datetime import datetime, timedelta
import logging
from typing import Optional

from . import ActionSchema, Action
from app.core.event_engine.events import Event, DeviceEventType, PlantEventType

import app.core.models as models
from app.core.services.alert_service import create_alert

from marshmallow import fields, post_load, INCLUDE
from marshmallow_enum import EnumField

#######################
# Schemas
#######################
class GenerateAlertActionSchema(ActionSchema):
	message_template = fields.Str()
	severity = EnumField(models.SeverityLevelEnum)

	class Meta:
		unknown = INCLUDE

	@post_load
	def make(self, data, **kwargs):
		return GenerateAlertAction(**data)

class GenerateDeviceAlertActionSchema(GenerateAlertActionSchema):
	class Meta:
		unknown = INCLUDE

	@post_load
	def make(self, data, **kwargs):
		return GenerateDeviceAlertAction(**data)

class GeneratePlantAlertActionSchema(GenerateAlertActionSchema):
	class Meta:
		unknown = INCLUDE

	@post_load
	def make(self, data, **kwargs):
		return GeneratePlantAlertAction(**data)
#######################

class GenerateAlertAction(Action):
	__schema__ = GenerateAlertActionSchema

	message_template: str
	severity: models.SeverityLevelEnum
	# TODO:
	# push_notification: bool

	def __init__(self, message_template: str, severity: models.SeverityLevelEnum, disabled: bool, action_id: Optional[int] = None, cooldown: timedelta | None = None, last_executed: datetime | None = None):
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

	def generate(self, event: Event) -> models.Alert:
		"""Generates an Alert object

		Args:
				event (Event): Event used to generate alert

		Returns:
				Alert: Generated Alert object
		"""
		message = self.generate_message(event)
		# TODO: add col for action id
		alert = models.Alert(message=message, severity=self.severity, action_id=self.action_id, time=datetime.now())
		return alert

	def execute(self, event: Event) -> bool:
		"""Executes action. Generates an Alert object and persists it in the database

		Args:
				event (Event): Event used to generate Alert

		Returns:
				bool: Whether or not action executed succesfully
		"""
		# this needs to be here because it will cause
		# import app.core.services as services

		logging.info('Executing GenerateAlertAction')
		if not self.can_execute():
			return False

		alert = self.generate(event)
		logging.info(f'Persisting alert: {alert}')

		# persist alert
		create_alert(event.user_id, alert, event.session)

		# TODO: push notification

		# update last executed time
		self.update_last_executed(event)

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