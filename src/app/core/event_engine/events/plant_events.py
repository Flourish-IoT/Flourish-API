from dataclasses import dataclass
from . import Event
import app.core.models as models

@dataclass
class PlantEventType(Event):
	plant: models.Plant

@dataclass
class SensorDataEvent(PlantEventType):
	data: models.SensorData