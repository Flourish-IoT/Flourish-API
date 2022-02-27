
from abc import ABC, abstractmethod
from datetime import timedelta
import logging
from typing import List
from sqlalchemy import Column
from app.core.event_engine import Field
from app.core.event_engine.handlers import EventHandler
from app.core.event_engine.events import Event, PlantEventType, DeviceEventType
from app.core.event_engine.queries import ValueQuery, SlopeQuery
from app.core.event_engine.post_process_functions import ValueRating, target_value_score, plant_value_score
from app.core.event_engine.handlers import SensorDataEventHandler
from app.core.event_engine.actions import GeneratePlantAlertAction
from app.core.event_engine.triggers import EqualsTrigger, AndTrigger, LessThanTrigger, GreaterThanTrigger

from app.core.models import SensorData, Plant, Device, SeverityLevelEnum
from app.core.models.plant_type import PlantType

def load_event_handlers(event: Event) -> List[EventHandler]:
	logging.info(f'Loading event handlers for event: {event}')

	handlers = []
	id_column: Column
	match event:
		case e if isinstance(e, PlantEventType):
			# e.plant_id
			pass
		case e if isinstance(e, DeviceEventType):
			pass
		case _:
			raise ValueError('Invalid event')

	# TODO: get config from db

	# TODO: get config overrides from db

	return handlers

def generate_default_plant_event_handlers(plant: Plant):
	return [
		SensorDataEventHandler(
			Field(SensorData.temperature, {
				'value': ValueQuery(SensorData, SensorData.plant_id, SensorData.time, plant_value_score(plant, PlantType.minimum_temperature, PlantType.maximum_temperature)),
				# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
			}),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooLow),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is too cold! Turn up the heat', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.Low),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is feeling cold. You should consider increasing the temperature', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				# EqualsTrigger(ValueRating.Nominal,
				# 	[]
				# ),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.High),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is feeling hot. You should consider decreasing the temperature', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooHigh),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is too hot! Lower the heat', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
			]
		),
		SensorDataEventHandler(
			Field(SensorData.humidity, {
				'value': ValueQuery(SensorData, SensorData.plant_id, SensorData.time, plant_value_score(plant, PlantType.minimum_temperature, PlantType.maximum_temperature)),
				# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
			}),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooLow),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('The air around {event.plant.name} is too dry! Try spraying it with water', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.Low),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('The air around {event.plant.name} is getting dry. You should consider spraying it with water', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				# EqualsTrigger(ValueRating.Nominal,
				# 	[]
				# ),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.High),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('The air around {event.plant.name} is getting humid. You should consider moving it to a dryer location', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooHigh),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('The air around {event.plant.name} is too humid! Move them to a dryer location', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
			]
		),
		SensorDataEventHandler(
			Field(SensorData.soil_moisture, {
				'value': ValueQuery(SensorData, SensorData.plant_id, SensorData.time, plant_value_score(plant, PlantType.minimum_temperature, PlantType.maximum_temperature)),
				# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
			}),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooLow),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} needs water', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.Low),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} needs water soon', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				# EqualsTrigger(ValueRating.Nominal,
				# 	[]
				# ),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.High),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} has too much water. Try watering less next time', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooHigh),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} has been overwatered! Move them to a dryer pot', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
			]
		),
		SensorDataEventHandler(
			Field(SensorData.light, {
				'value': ValueQuery(SensorData, SensorData.plant_id, SensorData.time, plant_value_score(plant, PlantType.minimum_temperature, PlantType.maximum_temperature)),
				# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
			}),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooLow),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} needs more light! Move them to a sunnier location', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.Low),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is not getting enough light. Try moving them to a sunnier location', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				# EqualsTrigger(ValueRating.Nominal,
				# 	[]
				# ),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.High),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is getting a lot of light. Try moving them to a shadier location', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooHigh),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is getting too much light! Move them to a shadier location', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
			]
		),
	]

def generate_default_device_event_handlers(device: Device):
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
	# TODO: get handlers from config
	# handlers = load_event_handlers(event)
	if isinstance(event, PlantEventType):
		handlers = generate_default_plant_event_handlers(event.plant)
	else:
		raise ValueError("Only plant event types are implemented")

	for handler in handlers:
		handler.handle(event)