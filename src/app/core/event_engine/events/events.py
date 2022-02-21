from abc import ABC
from dataclasses import dataclass
from typing import Any, List, Protocol

from app.core.event_engine.events.field import Field
from app.core.event_engine.events.triggers import Trigger

class Event:
	pass

###################################
# plant events
###################################
class PlantEventType:
	plant_id: int

@dataclass
class SensorDataEvent(Event, PlantEventType):
	pass

###################################
# device events
###################################
class DeviceEventType:
	device_id: int

@dataclass
class DeviceStateChangeEvent(Event, DeviceEventType):
	pass

@dataclass
class DeviceMetricEvent(Event, DeviceEventType):
	pass