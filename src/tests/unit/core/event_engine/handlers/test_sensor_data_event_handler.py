from app.core.event_engine import Field
from app.core.event_engine.handlers.sensor_data_event_handler import SensorDataEventHandler
from app.core.event_engine.handlers import EventHandler
from app.core.event_engine.events import *
from app.core.event_engine.triggers import Trigger
from app.core.models import Plant, SensorData
from unittest.mock import MagicMock
import pytest
from sqlalchemy import Column
from sqlalchemy.orm import Session

class TestSensorDataEventHandler:
	def test_handle(self):
		return_value = 3
		mock_field = MagicMock(Field)
		mock_field.get_value.return_value = return_value
		mock_trigger = MagicMock(Trigger)
		mock_trigger_2 = MagicMock(Trigger)
		handler = SensorDataEventHandler(mock_field, [mock_trigger, mock_trigger_2])

		plant_id = -1
		mock_session = MagicMock(Session)
		event = SensorDataEvent(
			user_id=-1,
			session=mock_session,
			plant=Plant(plant_id=plant_id),
			data=SensorData()
		)

		handler.handle(event)

		mock_field.get_value.assert_called_with(plant_id, mock_session)
		mock_trigger.execute.assert_called_with(return_value, event)
		mock_trigger_2.execute.assert_called_with(return_value, event)

	def test_no_handle(self):
		mock_field = MagicMock(Field)
		mock_field.get_value.return_value = 3
		mock_trigger = MagicMock(Trigger)
		mock_trigger_2 = MagicMock(Trigger)
		handler = SensorDataEventHandler(mock_field, [mock_trigger, mock_trigger_2])

		handler.handle(Event(user_id=-1, session=MagicMock(Session))) # type: ignore

		mock_field.get_value.assert_not_called()
		mock_trigger.execute.assert_not_called()
		mock_trigger_2.execute.assert_not_called()
