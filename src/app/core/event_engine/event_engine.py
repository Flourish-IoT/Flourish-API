
from abc import ABC, abstractmethod
from datetime import timedelta
import logging
from typing import List
from sqlalchemy import Column
from app.core.event_engine.events import Event, EventHandler, PlantEventType, DeviceEventType
from app.core.event_engine.events.field.field import Field
from app.core.event_engine.events.field.queries import ValueQuery, SlopeQuery
from app.core.event_engine.events.field.score_functions import TargetValueScoreFunction, ValueRating, target_value_score, PlantTypeMinMaxSource

from app.core.event_engine.events.handlers import SensorDataEventHandler
from app.core.event_engine.events.triggers.actions import GenerateAlertAction
from app.core.event_engine.events.triggers import EqualsTrigger, AndTrigger, LessThanTrigger, GreaterThanTrigger
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
				'value': ValueQuery(SensorData, SensorData.plant_id, SensorData.time, target_value_score(PlantTypeMinMaxSource(plant, PlantType.minimum_temperature, PlantType.maximum_temperature))),
				'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
			}),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooLow),
						LessThanTrigger(field='slope', value=0),
					],
					[GenerateAlertAction('{event.plant.name} is too cold! Turn up the heat', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.Low),
						LessThanTrigger(field='slope', value=0),
					],
					[GenerateAlertAction('{event.plant.name} is feeling cold. You should consider increasing the temperature', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				# EqualsTrigger(ValueRating.Nominal,
				# 	[]
				# ),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.High),
						GreaterThanTrigger(field='slope', value=0),
					],
					[GenerateAlertAction('{event.plant.name} is feeling hot. You should consider decreasing the temperature', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooHigh),
						GreaterThanTrigger(field='slope', value=0),
					],
					[GenerateAlertAction('{event.plant.name} is too hot! Lower the heat', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
			]
		),
		# SensorDataEventHandler(
		# 	Field(SensorData.temperature,
		# 		ValueQuery(SensorData, SensorData.plant_id, SensorData.time),
		# 		TargetValueScoreFunction(PlantTypeMinMaxSource(plant, PlantType.minimum_temperature, PlantType.maximum_temperature))
		# 	),
		# 	[
		# 		EqualsTrigger(ValueRating.TooLow,
		# 			[GenerateAlertAction('{event.plant.name} is too cold! Turn up the heat', SeverityLevelEnum.Critical, False, timedelta(days=1))]
		# 		),
		# 		EqualsTrigger(ValueRating.Low,
		# 			[GenerateAlertAction('{event.plant.name} is feeling cold. You should consider increasing the temperature', SeverityLevelEnum.Warning, False, timedelta(days=1))]
		# 		),
		# 		EqualsTrigger(ValueRating.Nominal,
		# 			[]
		# 		),
		# 		EqualsTrigger(ValueRating.High,
		# 			[GenerateAlertAction('{event.plant.name} is feeling hot. You should consider decreasing the temperature', SeverityLevelEnum.Warning, False, timedelta(days=1))]
		# 		),
		# 		EqualsTrigger(ValueRating.TooHigh,
		# 			[GenerateAlertAction('{event.plant.name} is too hot! Lower the heat', SeverityLevelEnum.Critical, False, timedelta(days=1))]
		# 		),
		# 	]
		# ),
		# SensorDataEventHandler(
		# 	Field(SensorData.humidity, ValueQuery(SensorData, SensorData.plant_id, SensorData.time), TargetValueScoreFunction), [ ]
		# ),
		# SensorDataEventHandler(
		# 	Field(SensorData.soil_moisture, ValueQuery(SensorData, SensorData.plant_id, SensorData.time), TargetValueScoreFunction), [ ]
		# ),
		# SensorDataEventHandler(
		# 	Field(SensorData.light, ValueQuery(SensorData, SensorData.plant_id, SensorData.time), TargetValueScoreFunction), [ ]
		# ),
	]

def generate_default_device_event_handlers(device: Device):
	# return [
	# 	SensorDataEventHandler(
	# 		Field(SensorData.temperature, ValueQuery(SensorData, SensorData.plant_id, SensorData.time), TargetValueScoreFunction(None, None)), [ ]
	# 	),
	# ]
	pass


def handle(event: Event):
	# TODO: get handlers from config
	handlers = load_event_handlers(event)

	for handler in handlers:
		handler.handle(event)