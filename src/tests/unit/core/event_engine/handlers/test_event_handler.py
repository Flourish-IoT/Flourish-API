from app.core.event_engine.queries import Query
from app.core.event_engine.handlers import EventHandler
from app.core.event_engine.events import *
from app.core.models import Plant, Device
from unittest.mock import MagicMock
import pytest
from sqlalchemy import Column
from sqlalchemy.orm import Session

def _get_mock_query(v):
	mock =  MagicMock(Query)
	mock.execute.return_value = v
	return mock

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
		handler = ConcreteEventHandler({}, [])
		handler.supported_events = handled_events

		assert handler.can_handle(event) == expected

	@pytest.mark.parametrize('expected, queries', [
		({'foo': 5}, { 'foo': _get_mock_query(5) }),
		({'foo': 5, 'bar': 20}, { 'foo': _get_mock_query(5), 'bar': _get_mock_query(20) }),
		({'foo': 20}, { 'foo': _get_mock_query(5), 'foo': _get_mock_query(20) }),
	])
	def test_get_values(self, expected, queries: dict):
		"""Ensure get_value returns the proper response"""
		handler = ConcreteEventHandler(queries, [])
		mock_session = MagicMock(Session)
		mock_event = MagicMock(Event)
		value = handler.get_values(1, mock_session, mock_event)

		# make sure queries are called with correct values
		for query in queries.values():
			query.execute.assert_called_once_with(1, mock_session, mock_event)

		# make sure returned value is correct
		assert value == expected
