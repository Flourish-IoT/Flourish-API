from dataclasses import dataclass
# from app.core.event_engine.events import Event
from . import event
import app.core.models as models
# from app.core.models import Device

@dataclass
class DeviceEventType(event.Event):
	device: models.Device

@dataclass
class DeviceStateChangeEvent(DeviceEventType):
	pass

@dataclass
class DeviceMetricEvent(DeviceEventType):
	pass
