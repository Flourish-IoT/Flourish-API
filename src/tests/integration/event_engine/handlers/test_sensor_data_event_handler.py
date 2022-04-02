from datetime import datetime, timedelta
from unittest import mock
from app.core.event_engine import Field
from app.core.event_engine.events import SensorDataEvent
from app.core.event_engine.queries import ValueQuery, SlopeQuery
from app.core.event_engine.post_process_functions import ValueRating, plant_value_score
from app.core.event_engine.handlers import SensorDataEventHandler
from app.core.event_engine.actions import GeneratePlantAlertAction
from app.core.event_engine.triggers import EqualsTrigger, AndTrigger, LessThanTrigger
from app.core.models import Plant, SensorData, SeverityLevelEnum, Alert, PlantType
from unittest.mock import MagicMock
import pytest
from sqlalchemy import Column
from sqlalchemy.orm.scoping import ScopedSession
from freezegun import freeze_time

# freeze time so we can compare timestamps
freezer = freeze_time()
freezer.start()

class TestSensorDataEventHandler:
	def _handle(self, session, plant, sensor_data):
		handler = SensorDataEventHandler(
			Field(
				SensorData.temperature, {
					'value': ValueQuery(SensorData, SensorData.plant_id, SensorData.time, plant_value_score(plant, PlantType.minimum_temperature, PlantType.maximum_temperature)),
					'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
				}
			),
			[
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooLow),
						LessThanTrigger(field='slope', value=0)
					],
					[GeneratePlantAlertAction('{event.plant.name} is too cold! Turn up the heat', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.Low),
						# LessThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is feeling cold. You should consider increasing the temperature', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.High),
						# GreaterThanTrigger(field='slope', value=0),
					],
					[GeneratePlantAlertAction('{event.plant.name} is feeling hot. You should consider decreasing the temperature', SeverityLevelEnum.Warning, False, timedelta(days=1))]
				),
				AndTrigger([
						EqualsTrigger(field='value', value=ValueRating.TooHigh),
						# GreaterThanTrigger(field='slope', value=0)
					],
					[GeneratePlantAlertAction('{event.plant.name} is too hot! Lower the heat', SeverityLevelEnum.Critical, False, timedelta(days=1))]
				)
			]
		)

		event = SensorDataEvent(
			user_id=-1,
			session=session,
			plant=plant,
			data=sensor_data
		)

		handler.handle(event)

	# TODO: remake these tests when plant rating is finished
	@pytest.mark.parametrize('plant, sensor_data, query_results, expected', [
		(
			Plant(plant_id=-1, user_id = -1, device_id = -1, plant_type_id = -1, name = 'George', plant_type=PlantType(
				minimum_temperature = 40, maximum_temperature = 80
			)),
			SensorData(plant_id = -1, time = datetime.now(), temperature = 20, humidity = 23.4, soil_moisture = 20, light = 120_000),
			[20, -2],
			Alert(message='George is too cold! Turn up the heat', severity=SeverityLevelEnum.Critical, time=datetime.now(), plant_id=-1, user_id=-1)
		),
		(
			Plant(plant_id=-1, user_id = -1, device_id = -1, plant_type_id = -1, name = 'George', plant_type=PlantType(
				minimum_temperature = 40, maximum_temperature = 80
			)),
			SensorData(plant_id = -1, time = datetime.now(), temperature = 90, humidity = 23.4, soil_moisture = 20, light = 120_000),
			[90, 2],
			Alert(message='George is too hot! Lower the heat', severity=SeverityLevelEnum.Critical, time=datetime.now(), plant_id=-1, user_id=-1)
		),
		(
			Plant(plant_id=-1, user_id = -1, device_id = -1, plant_type_id = -1, name = 'George', plant_type=PlantType(
				minimum_temperature = 40, maximum_temperature = 80
			)),
			SensorData(plant_id = -1, time = datetime.now(), temperature = 60, humidity = 23.4, soil_moisture = 20, light = 120_000),
			[60, 2],
			None
		)
	])
	def test_handle_no_db(self, plant, sensor_data, query_results, expected):
		mock_session = MagicMock(ScopedSession)
		mock_session.execute.return_value.scalar_one.side_effect = query_results

		self._handle(mock_session, plant, sensor_data)

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


