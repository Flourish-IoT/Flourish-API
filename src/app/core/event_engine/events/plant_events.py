from dataclasses import dataclass
from . import event
# from app.core.event_engine.events import Event
import app.core.models as models

@dataclass
class PlantEventType(event.Event):
	plant: models.Plant

@dataclass
class SensorDataEvent(PlantEventType):
	data: models.SensorData