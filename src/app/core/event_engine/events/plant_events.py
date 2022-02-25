from dataclasses import dataclass
from app.core.event_engine.events import Event
from app.core.models import Plant, SensorData

@dataclass
class PlantEventType(Event):
	plant: Plant

@dataclass
class SensorDataEvent(PlantEventType):
	data: SensorData