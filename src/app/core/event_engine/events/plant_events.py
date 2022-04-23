from __future__ import annotations
from dataclasses import dataclass
from . import Event
from app.core.models import Plant, SensorData

@dataclass
class PlantEventType(Event):
	plant: Plant

@dataclass
class SensorDataEvent(PlantEventType):
	data: SensorData