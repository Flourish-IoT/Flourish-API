from dataclasses import dataclass

from app.core.models import Plant, Device, SensorData
from sqlalchemy.orm.scoping import ScopedSession

@dataclass
class Event:
	user_id: int
	session: ScopedSession

###################################
# plant events
###################################
@dataclass
class PlantEventType:
	plant: Plant

@dataclass
class SensorDataEvent(Event, PlantEventType):
	data: SensorData

###################################
# device events
###################################
@dataclass
class DeviceEventType:
	device: Device

@dataclass
class DeviceStateChangeEvent(Event, DeviceEventType):
	pass

@dataclass
class DeviceMetricEvent(Event, DeviceEventType):
	pass