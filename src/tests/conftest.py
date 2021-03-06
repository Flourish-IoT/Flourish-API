# hack to make pytest import correctly
from copy import copy, deepcopy
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from alembic.command import upgrade
from alembic.config import Config

import pytest
from app import Environment, db, create_rest_app
from app.common.schemas.dynamic_field import DynamicField
from app.common.schemas.dynamic_schema import DynamicSchema
from app.common.schemas.type_field import TypeField
import app.core.models as models

from app.core.event_engine.queries import ValueQuery, SlopeQuery
from app.core.event_engine.post_process_functions import ValueRating, PlantValueScore
from app.core.event_engine.handlers import SensorDataEventHandler
from app.core.event_engine.actions import GeneratePlantAlertAction
from app.core.event_engine.triggers import EqualsTrigger, AndTrigger, LessThanTrigger

@pytest.fixture(scope='session')
def app():
	app = create_rest_app(Environment.test)
	yield app

@pytest.fixture(scope='session')
def app_context(app):
	with app.app_context():
		yield

@pytest.fixture(scope='session')
def db_context(app_context):
	# run migrations
	config = Config('alembic.ini')
	upgrade(config, 'head')

@pytest.fixture(scope='function', autouse=True)
def session(db_context):
	connection = db.engine.connect()
	transaction = connection.begin()

	options = {
		'bind': connection,
		'binds': {}
	}
	session_ = db.create_scoped_session(options=options)

	db.session = session_
	yield session_

	transaction.rollback()
	connection.close()
	session_.remove()

	# return db.session


@pytest.fixture()
def client(app):
	return app.test_client()

@pytest.fixture
def default_plant():
	return models.Plant(plant_id=-1, user_id = -1, device_id = -1, plant_type_id = -1, name = 'George', plant_type=models.PlantType(
		minimum_temperature = 40, maximum_temperature = 80
	))

@pytest.fixture
def default_handler():
	return SensorDataEventHandler({
			'value': ValueQuery(models.SensorData, models.SensorData.temperature, models.SensorData.plant_id, models.SensorData.time, PlantValueScore(models.PlantType.minimum_temperature, models.PlantType.maximum_temperature)),
			'slope': SlopeQuery(models.SensorData, models.SensorData.temperature, models.SensorData.plant_id, timedelta(hours=3))
		},
		[
			AndTrigger([
					EqualsTrigger(field='value', value=ValueRating.TooLow),
					LessThanTrigger(field='slope', value=0)
				],
				[GeneratePlantAlertAction('{event.plant.name} is too cold! Turn up the heat', models.SeverityLevelEnum.Critical, False, action_id = 1, cooldown=timedelta(days=1))]
			),
			AndTrigger([
					EqualsTrigger(field='value', value=ValueRating.Low),
					# LessThanTrigger(field='slope', value=0),
				],
				[GeneratePlantAlertAction('{event.plant.name} is feeling cold. You should consider increasing the temperature', models.SeverityLevelEnum.Warning, False, action_id = 2, cooldown=timedelta(days=1))]
			),
			AndTrigger([
					EqualsTrigger(field='value', value=ValueRating.High),
					# GreaterThanTrigger(field='slope', value=0),
				],
				[GeneratePlantAlertAction('{event.plant.name} is feeling hot. You should consider decreasing the temperature', models.SeverityLevelEnum.Warning, False, action_id = 3, cooldown=timedelta(days=1))]
			),
			AndTrigger([
					EqualsTrigger(field='value', value=ValueRating.TooHigh),
					# GreaterThanTrigger(field='slope', value=0)
				],
				[GeneratePlantAlertAction('{event.plant.name} is too hot! Lower the heat', models.SeverityLevelEnum.Critical, False, action_id = 4, cooldown=timedelta(days=1))]
			)
		]
	)

# automatically restore schemas inbetween tests
@pytest.fixture(autouse=True)
def clean_schema():
	dynamic_schema_prev_schemas = deepcopy(DynamicSchema.type_schemas)
	type_field_prev_mapping = deepcopy(TypeField.type_name_mapping)
	dynamic_field_prev_type = deepcopy(DynamicField.type_mapping)
	dynamic_field_prev_name = deepcopy(DynamicField.type_name_mapping)

	yield # test runs

	DynamicSchema.type_schemas = dynamic_schema_prev_schemas
	TypeField.type_name_mapping = type_field_prev_mapping
	DynamicField.type_mapping = dynamic_field_prev_type
	DynamicField.type_name_mapping = dynamic_field_prev_name


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

@pytest.fixture(scope='function')
def user(session):
	# TODO: use actual password hash?
	user = models.User(email='foo@bar.com', username='George', password_hash='123', user_verified=True)
	session.add(user)
	session.commit()
	return user

@pytest.fixture(scope='function')
def device(session, user):
	device = models.Device(user_id=user.user_id, device_type=models.DeviceTypeEnum.Sensor, device_state=models.DeviceStateEnum.Connected, api_version='1.2.3', software_version='3.2.1', name='Paul', model='Flourish Device')
	session.add(device)
	session.commit()
	return device

@pytest.fixture(scope='function')
def plant(session, user, device):
	# TODO: add plant_type_id (another fixture?)
	plant = models.Plant(user_id=user.user_id, device_id=device.device_id, plant_type_id=None, name='Momo')
	session.add(plant)
	session.commit()
	return plant