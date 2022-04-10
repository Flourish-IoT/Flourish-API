# hack to make pytest import correctly
from datetime import datetime, timedelta
from unittest.mock import MagicMock
import pytest
from app import Environment, db, create_rest_app
from app.core.event_engine import Field
from app.core.event_engine.queries import ValueQuery, SlopeQuery
from app.core.event_engine.post_process_functions import ValueRating, PlantValueScore
from app.core.event_engine.handlers import SensorDataEventHandler
from app.core.event_engine.actions import GeneratePlantAlertAction
from app.core.event_engine.triggers import EqualsTrigger, AndTrigger, LessThanTrigger
from app.core.models import Plant, SensorData, SeverityLevelEnum, PlantType

@pytest.fixture(scope='session')
def app():
	# TODO: this should be Environment.test when we figure out how it will work
	a = create_rest_app(Environment.local)
	with a.app_context():
		yield

	return

@pytest.fixture
def session(app):
	return db.session

@pytest.fixture
def default_plant():
	return Plant(plant_id=-1, user_id = -1, device_id = -1, plant_type_id = -1, name = 'George', plant_type=PlantType(
		minimum_temperature = 40, maximum_temperature = 80
	))

@pytest.fixture
def default_handler(default_plant):
	return SensorDataEventHandler(
		Field(
			SensorData.temperature, {
				'value': ValueQuery(SensorData, SensorData.plant_id, SensorData.time, PlantValueScore(PlantType.minimum_temperature, PlantType.maximum_temperature)),
				'slope': SlopeQuery(SensorData, SensorData.plant_id, timedelta(hours=3))
			}
		),
		[
			AndTrigger([
					EqualsTrigger(field='value', value=ValueRating.TooLow),
					LessThanTrigger(field='slope', value=0)
				],
				[GeneratePlantAlertAction('{event.plant.name} is too cold! Turn up the heat', SeverityLevelEnum.Critical, False, action_id = 1, cooldown=timedelta(days=1))]
			),
			AndTrigger([
					EqualsTrigger(field='value', value=ValueRating.Low),
					# LessThanTrigger(field='slope', value=0),
				],
				[GeneratePlantAlertAction('{event.plant.name} is feeling cold. You should consider increasing the temperature', SeverityLevelEnum.Warning, False, action_id = 2, cooldown=timedelta(days=1))]
			),
			AndTrigger([
					EqualsTrigger(field='value', value=ValueRating.High),
					# GreaterThanTrigger(field='slope', value=0),
				],
				[GeneratePlantAlertAction('{event.plant.name} is feeling hot. You should consider decreasing the temperature', SeverityLevelEnum.Warning, False, action_id = 3, cooldown=timedelta(days=1))]
			),
			AndTrigger([
					EqualsTrigger(field='value', value=ValueRating.TooHigh),
					# GreaterThanTrigger(field='slope', value=0)
				],
				[GeneratePlantAlertAction('{event.plant.name} is too hot! Lower the heat', SeverityLevelEnum.Critical, False, action_id = 4, cooldown=timedelta(days=1))]
			)
		]
	)





def pytest_addoption(parser):
	parser.addoption('--db', action="store_true", default=False, help='Run tests against database')

def pytest_configure(config):
	config.addinivalue_line("markers", "db: Mark tests as db to run")

def pytest_collection_modifyitems(config, items):
	if config.getoption('--db'):
		# --db passed, do not skip tests that require the database
		return

	skip_db = pytest.mark.skip(reason='Need --db option to run')
	for item in items:
		if 'db' in item.keywords:
			item.add_marker(skip_db)