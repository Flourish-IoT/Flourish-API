from dataclasses import dataclass
from app.core.event_engine.events import Event
from app.core.models import Device

@dataclass
class DeviceEventType(Event):
	device: Device

@dataclass
class DeviceStateChangeEvent(DeviceEventType):
	pass

@dataclass
class DeviceMetricEvent(DeviceEventType):
	pass
