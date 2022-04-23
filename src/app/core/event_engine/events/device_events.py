from __future__ import annotations
from dataclasses import dataclass
from . import Event
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
