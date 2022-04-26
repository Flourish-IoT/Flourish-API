from datetime import datetime, timedelta
from unittest import mock
from app.common.schemas.dynamic_schema import DynamicSchema
from app.core.event_engine import Field
from app.core.event_engine.events import SensorDataEvent
from app.core.event_engine.queries import ValueQuery, SlopeQuery
from app.core.event_engine.post_process_functions import ValueRating
from app.core.event_engine.handlers import SensorDataEventHandler
from app.core.event_engine.actions import GeneratePlantAlertAction
from app.core.event_engine.triggers import EqualsTrigger, AndTrigger, LessThanTrigger
from app.core.models import Plant, SensorData, SeverityLevelEnum, Alert, PlantType
from unittest.mock import MagicMock
import pytest
from sqlalchemy import Column
from sqlalchemy.orm.scoping import ScopedSession
from freezegun import freeze_time

cur_time = datetime.now()

@freeze_time(cur_time)
class TestSensorDataEventHandler:
	def _handle(self, handler, session, plant, sensor_data):
		event = SensorDataEvent(
			user_id=-1,
			session=session,
			plant=plant,
			data=sensor_data
		)

		handler.handle(event)

	# TODO: remake these tests when plant rating is finished
	@pytest.mark.parametrize('sensor_data, query_results, expected', [
		(
			SensorData(plant_id = -1, time = cur_time, temperature = 20, humidity = 23.4, soil_moisture = 20, light = 120_000),
			[20, -2],
			Alert(message='George is too cold! Turn up the heat', severity=SeverityLevelEnum.Critical, time=cur_time, plant_id=-1, user_id=-1, action_id=1)
		),
		(
			SensorData(plant_id = -1, time = cur_time, temperature = 90, humidity = 23.4, soil_moisture = 20, light = 120_000),
			[90, 2],
			Alert(message='George is too hot! Lower the heat', severity=SeverityLevelEnum.Critical, time=cur_time, plant_id=-1, user_id=-1, action_id=4)
		),
		(
			SensorData(plant_id = -1, time = cur_time, temperature = 60, humidity = 23.4, soil_moisture = 20, light = 120_000),
			[60, 2],
			None
		)
	])
	def test_handle_no_db(self, default_handler, default_plant, sensor_data, query_results, expected):
		mock_session = MagicMock(ScopedSession)
		mock_session.execute.return_value.scalar_one.side_effect = query_results

		self._handle(default_handler, mock_session, default_plant, sensor_data)

		if expected is None:
			mock_session.add.assert_not_called()
		else:
			mock_session.add.assert_called_once_with(expected)

	# def test_no_handle(self):
	# 	mock_field = MagicMock(Field)
	# 	mock_field.get_value.return_value = 3
	# 	mock_trigger = MagicMock(Trigger)
	# 	mock_trigger_2 = MagicMock(Trigger)
	# 	handler = SensorDataEventHandler(mock_field, [mock_trigger, mock_trigger_2])

	# 	handler.handle(Event(user_id=-1, session=MagicMock(Session))) # type: ignore

	# 	mock_field.get_value.assert_not_called()
	# 	mock_trigger.execute.assert_not_called()
	# 	mock_trigger_2.execute.assert_not_called()


