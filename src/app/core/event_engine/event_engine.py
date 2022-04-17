from datetime import timedelta
from typing import List, cast
from sqlalchemy import Column, Integer
import app.core.models as models
import app.core.models.event_engine as event_engine_models
import app.core.services.event_handler_service as services
from app.core.event_engine import Field
from app.core.event_engine.handlers import EventHandler
from app.core.event_engine.events import Event, PlantEventType, DeviceEventType
from app.core.event_engine.queries import ValueQuery, SlopeQuery
from app.core.event_engine.post_process_functions import ValueRating, target_value_score, PlantValueScore
from app.core.event_engine.handlers import SensorDataEventHandler
from app.core.event_engine.actions import GeneratePlantAlertAction
from app.core.event_engine.triggers import EqualsTrigger, AndTrigger, LessThanTrigger, GreaterThanTrigger

import logging
logger = logging.getLogger(__name__)

def load_event_handlers(event: Event) -> List[EventHandler]:
	logger.info(f'Loading event handlers for event: {event}')

	# use event type to determine id and column to find event handlers
	id: int
	id_column: Column[Integer]
	match event:
		case e if isinstance(e, PlantEventType):
			id = e.plant.plant_id
			id_column = cast(Column[Integer], event_engine_models.EventHandlerInformation.plant_id)
		case e if isinstance(e, DeviceEventType):
			id = e.device.device_id
			id_column = cast(Column[Integer], event_engine_models.EventHandlerInformation.device_id)
		case _:
			raise ValueError('Invalid event')

	# get event handler configs from db
	return services.get_event_handlers(id, id_column, event.session)

def generate_default_plant_event_handlers():
	# TODO: batch queries?
	# TODO: once the plant value rating is part of the plant table, get directly from the event instead of DB
	return [
		SensorDataEventHandler(
			Field(models.SensorData.temperature, {
				'value': ValueQuery(models.SensorData, models.SensorData.plant_id, models.SensorData.time, PlantValueScore(models.PlantType.minimum_temperature, models.PlantType.maximum_temperature)),
				# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
			}),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooLow),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is too cold! Turn up the heat', models.SeverityLevelEnum.Critical, False, cooldown=timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.Low),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is feeling cold. You should consider increasing the temperature', models.SeverityLevelEnum.Warning, False, cooldown=timedelta(days=1))]
				),
				# EqualsTrigger(ValueRating.Nominal,
				# 	[]
				# ),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.High),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is feeling hot. You should consider decreasing the temperature', models.SeverityLevelEnum.Warning, False, cooldown=timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooHigh),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is too hot! Lower the heat', models.SeverityLevelEnum.Critical, False, cooldown=timedelta(days=1))]
				),
			]
		),
		SensorDataEventHandler(
			Field(models.SensorData.humidity, {
				'value': ValueQuery(models.SensorData, models.SensorData.plant_id, models.SensorData.time, PlantValueScore(models.PlantType.minimum_temperature, models.PlantType.maximum_temperature)),
				# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
			}),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooLow),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('The air around {event.plant.name} is too dry! Try spraying it with water', models.SeverityLevelEnum.Critical, False, cooldown=timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.Low),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('The air around {event.plant.name} is getting dry. You should consider spraying it with water', models.SeverityLevelEnum.Warning, False, cooldown=timedelta(days=1))]
				),
				# EqualsTrigger(ValueRating.Nominal,
				# 	[]
				# ),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.High),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('The air around {event.plant.name} is getting humid. You should consider moving it to a dryer location', models.SeverityLevelEnum.Warning, False, cooldown=timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooHigh),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('The air around {event.plant.name} is too humid! Move them to a dryer location', models.SeverityLevelEnum.Critical, False, cooldown=timedelta(days=1))]
				),
			]
		),
		SensorDataEventHandler(
			Field(models.SensorData.soil_moisture, {
				'value': ValueQuery(models.SensorData, models.SensorData.plant_id, models.SensorData.time, PlantValueScore(models.PlantType.minimum_temperature, models.PlantType.maximum_temperature)),
				# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
			}),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooLow),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} needs water', models.SeverityLevelEnum.Critical, False, cooldown=timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.Low),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} needs water soon', models.SeverityLevelEnum.Warning, False, cooldown=timedelta(days=1))]
				),
				# EqualsTrigger(ValueRating.Nominal,
				# 	[]
				# ),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.High),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} has too much water. Try watering less next time', models.SeverityLevelEnum.Warning, False, cooldown=timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooHigh),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} has been overwatered! Move them to a drier pot', models.SeverityLevelEnum.Critical, False, cooldown=timedelta(days=1))]
				),
			]
		),
		SensorDataEventHandler(
			Field(models.SensorData.light, {
				'value': ValueQuery(models.SensorData, models.SensorData.plant_id, models.SensorData.time, PlantValueScore(models.PlantType.minimum_temperature, models.PlantType.maximum_temperature)),
				# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
			}),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooLow),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} needs more light! Move them to a sunnier location', models.SeverityLevelEnum.Critical, False, cooldown=timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.Low),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is not getting enough light. Try moving them to a sunnier location', models.SeverityLevelEnum.Warning, False, cooldown=timedelta(days=1))]
				),
				# EqualsTrigger(ValueRating.Nominal,
				# 	[]
				# ),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.High),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is getting a lot of light. Try moving them to a shadier location', models.SeverityLevelEnum.Warning, False, cooldown=timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooHigh),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is getting too much light! Move them to a shadier location', models.SeverityLevelEnum.Critical, False, cooldown=timedelta(days=1))]
				),
			]
		),
	]

def generate_default_device_event_handlers(device: models.Device):
	# TODO: finish this
	raise NotImplementedError()
	# return [
	# 	SensorDataEventHandler(
	# 		Field(SensorData.temperature, ValueQuery(SensorData, SensorData.plant_id, SensorData.time), TargetValueScoreFunction(None, None)), [ ]
	# 	),
	# ]
	pass


def handle(event: Event):
	"""Handles an event

	Args:
			event (Event): Event to handle
	"""
	if isinstance(event, PlantEventType):
		handlers = load_event_handlers(event)
		logger.info(f'Found {len(handlers)} handlers for event {event}')
	else:
		raise ValueError("Only plant event types are implemented")

	for handler in handlers:
		handler.handle(event)