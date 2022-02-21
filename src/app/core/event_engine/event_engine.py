
from abc import ABC, abstractmethod
import logging
from typing import List
from app.core.event_engine.events import Event, EventHandler, PlantEventType, DeviceEventType
from sqlalchemy import Column
from app.core.event_engine.events.field.field import Field
from app.core.event_engine.events.field.queries import ValueQuery
from app.core.event_engine.events.field.score_functions import TargetValueScoreFunction

from app.core.event_engine.events.handlers import SensorDataEventHandler
from app.core.models import SensorData

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

	return handlers

def generate_default_plant_event_handlers():
	return [
		SensorDataEventHandler(
			Field(SensorData.temperature, ValueQuery(SensorData, SensorData.plant_id, SensorData.time), TargetValueScoreFunction), [ ]
		),
		SensorDataEventHandler(
			Field(SensorData.humidity, ValueQuery(SensorData, SensorData.plant_id, SensorData.time), TargetValueScoreFunction), [ ]
		),
		SensorDataEventHandler(
			Field(SensorData.soil_moisture, ValueQuery(SensorData, SensorData.plant_id, SensorData.time), TargetValueScoreFunction), [ ]
		),
		SensorDataEventHandler(
			Field(SensorData.light, ValueQuery(SensorData, SensorData.plant_id, SensorData.time), TargetValueScoreFunction), [ ]
		),
	]

def handle(event: Event):
	# TODO: get handlers from config
	handlers = load_event_handlers(event)

	for handler in handlers:
		handler.handle(event)