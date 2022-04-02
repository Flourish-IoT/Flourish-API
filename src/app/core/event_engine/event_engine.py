
from abc import ABC, abstractmethod
from datetime import timedelta
import logging
from typing import List, cast
from sqlalchemy import Column, Integer
from app.core.event_engine import Field
from app.core.event_engine.handlers import EventHandler
from app.core.event_engine.events import Event, PlantEventType, DeviceEventType
from app.core.event_engine.queries import ValueQuery, SlopeQuery
from app.core.event_engine.post_process_functions import ValueRating, target_value_score, plant_value_score
from app.core.event_engine.handlers import SensorDataEventHandler
from app.core.event_engine.actions import GeneratePlantAlertAction
from app.core.event_engine.triggers import EqualsTrigger, AndTrigger, LessThanTrigger, GreaterThanTrigger
import app.core.models as models
import app.core.models.event_engine as event_engine_models
import app.core.services.event_handler_service as services

def hydrate_event_handler(event_info: event_engine_models.EventHandlerInformation, actions: List[event_engine_models.ActionInformation]):
	action_map = {action.action_id: action.to_action() for action in actions}
	return event_info.to_event_handler(action_map)

def load_event_handlers(event: Event) -> List[EventHandler]:
	logging.info(f'Loading event handlers for event: {event}')

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
	event_handlers = []
	event_handler_information = services.get_event_handler_information(id, id_column, event.session)
	for event_handler_info in event_handler_information:
		actions = services.get_event_handler_actions(event_handler_info.event_handler_id, event.session)
		event_handler = hydrate_event_handler(event_handler_info, actions)
		event_handlers.append(event_handler)

	return event_handlers

# def save_event_handlers(event: Event)

def generate_default_plant_event_handlers(plant: models.Plant):
	# TODO: batch queries?
	return [
		SensorDataEventHandler(
			Field(models.SensorData.temperature, {
				'value': ValueQuery(models.SensorData, models.SensorData.plant_id, models.SensorData.time, processing.plant_value_score(plant, models.PlantType.minimum_temperature, models.PlantType.maximum_temperature)),
				# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
			}),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=models.ValueRating.TooLow),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is too cold! Turn up the heat', models.SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=models.ValueRating.Low),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is feeling cold. You should consider increasing the temperature', models.SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				# EqualsTrigger(ValueRating.Nominal,
				# 	[]
				# ),
				AndTrigger([
						EqualsTrigger(field='value', value=models.ValueRating.High),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is feeling hot. You should consider decreasing the temperature', models.SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=models.ValueRating.TooHigh),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is too hot! Lower the heat', models.SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
			]
		),
		# SensorDataEventHandler(
		# 	Field(models.SensorData.humidity, {
		# 		'value': ValueQuery(models.SensorData, models.SensorData.plant_id, models.SensorData.time, plant_value_score(plant, models.PlantType.minimum_temperature, models.PlantType.maximum_temperature)),
		# 		# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
		# 	}),
		# 	[
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.TooLow),
		# 				# LessThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('The air around {event.plant.name} is too dry! Try spraying it with water', models.SeverityLevelEnum.Critical, False, timedelta(days=1))]
		# 		),
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.Low),
		# 				# LessThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('The air around {event.plant.name} is getting dry. You should consider spraying it with water', models.SeverityLevelEnum.Warning, False, timedelta(days=1))]
		# 		),
		# 		# EqualsTrigger(ValueRating.Nominal,
		# 		# 	[]
		# 		# ),
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.High),
		# 				# GreaterThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('The air around {event.plant.name} is getting humid. You should consider moving it to a dryer location', models.SeverityLevelEnum.Warning, False, timedelta(days=1))]
		# 		),
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.TooHigh),
		# 				# GreaterThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('The air around {event.plant.name} is too humid! Move them to a dryer location', models.SeverityLevelEnum.Critical, False, timedelta(days=1))]
		# 		),
		# 	]
		# ),
		# SensorDataEventHandler(
		# 	Field(SensorData.soil_moisture, {
		# 		'value': ValueQuery(SensorData, SensorData.plant_id, SensorData.time, plant_value_score(plant, PlantType.minimum_temperature, PlantType.maximum_temperature)),
		# 		# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
		# 	}),
		# 	[
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.TooLow),
		# 				# LessThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('{event.plant.name} needs water', SeverityLevelEnum.Critical, False, timedelta(days=1))]
		# 		),
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.Low),
		# 				# LessThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('{event.plant.name} needs water soon', SeverityLevelEnum.Warning, False, timedelta(days=1))]
		# 		),
		# 		# EqualsTrigger(ValueRating.Nominal,
		# 		# 	[]
		# 		# ),
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.High),
		# 				# GreaterThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('{event.plant.name} has too much water. Try watering less next time', SeverityLevelEnum.Warning, False, timedelta(days=1))]
		# 		),
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.TooHigh),
		# 				# GreaterThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('{event.plant.name} has been overwatered! Move them to a drier pot', SeverityLevelEnum.Critical, False, timedelta(days=1))]
		# 		),
		# 	]
		# ),
		# SensorDataEventHandler(
		# 	Field(SensorData.light, {
		# 		'value': ValueQuery(SensorData, SensorData.plant_id, SensorData.time, plant_value_score(plant, PlantType.minimum_temperature, PlantType.maximum_temperature)),
		# 		# 'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
		# 	}),
		# 	[
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.TooLow),
		# 				# LessThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('{event.plant.name} needs more light! Move them to a sunnier location', SeverityLevelEnum.Critical, False, timedelta(days=1))]
		# 		),
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.Low),
		# 				# LessThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('{event.plant.name} is not getting enough light. Try moving them to a sunnier location', SeverityLevelEnum.Warning, False, timedelta(days=1))]
		# 		),
		# 		# EqualsTrigger(ValueRating.Nominal,
		# 		# 	[]
		# 		# ),
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.High),
		# 				# GreaterThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('{event.plant.name} is getting a lot of light. Try moving them to a shadier location', SeverityLevelEnum.Warning, False, timedelta(days=1))]
		# 		),
		# 		AndTrigger([
		# 				EqualsTrigger(field='value', value=ValueRating.TooHigh),
		# 				# GreaterThanTrigger(field='slope', value=0),
		# 			],
		# 			[GeneratePlantAlertAction('{event.plant.name} is getting too much light! Move them to a shadier location', SeverityLevelEnum.Critical, False, timedelta(days=1))]
		# 		),
		# 	]
		# ),
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
	# TODO: get handlers from config
	# handlers = load_event_handlers(event)
	if isinstance(event, PlantEventType):
		handlers = generate_default_plant_event_handlers(event.plant)
	else:
		raise ValueError("Only plant event types are implemented")

	for handler in handlers:
		handler.handle(event)