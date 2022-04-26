from app.core.event_engine import Field
from app.core.event_engine.handlers import EventHandler
from app.core.event_engine.events import *
from app.core.models import Plant, Device
from unittest.mock import MagicMock
import pytest
from sqlalchemy import Column
from sqlalchemy.orm import Session

class ConcreteEventHandler(EventHandler):
	def handle(self, event: Event):
		pass

class TestEventHandler:
	@pytest.mark.parametrize('handled_events, event, expected', [
		([Event], Event(user_id=-1, session=MagicMock(Session)), True),
		([PlantEventType], PlantEventType(user_id=-1, session=MagicMock(Session), plant=MagicMock(Plant)), True),
		([PlantEventType, DeviceEventType], PlantEventType(user_id=-1, session=MagicMock(Session), plant=MagicMock(Plant)), True),
		([PlantEventType, DeviceEventType], DeviceEventType(user_id=-1, session=MagicMock(Session), device=MagicMock(Device)), True),

		([Event], PlantEventType(user_id=-1, session=MagicMock(Session), plant=MagicMock(Plant)), False),
		([PlantEventType, Event], DeviceEventType(user_id=-1, session=MagicMock(Session), device=MagicMock(Device)), False),
	])
	def test_can_handle(self, event, handled_events, expected):
		"""Ensure can_handle returns the proper response"""
		mock_field = MagicMock(Field)
		handler = ConcreteEventHandler(mock_field, [])
		handler.supported_events = handled_events

		assert handler.can_handle(event) == expected