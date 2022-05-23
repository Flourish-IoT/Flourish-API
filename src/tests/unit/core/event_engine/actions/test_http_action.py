from datetime import datetime, timedelta
from app.core.event_engine.actions.http_action import HTTPActionSchema
from app.core.models import SeverityLevelEnum, Plant, SensorData
from app.core.event_engine.events import SensorDataEvent
from app.core.event_engine.actions import HTTPAction
from unittest.mock import MagicMock, patch
from sqlalchemy.orm.scoping import ScopedSession
import pytest

class TestHTTPAction:
	@pytest.mark.parametrize('value, event, expected', [
			(
				'{event.plant.name}',
				SensorDataEvent(-1, MagicMock(ScopedSession), Plant(name='Frodo'), SensorData(plant_id=-1, time=datetime.now(), temperature=70, humidity=40, soil_moisture=20, light=100_000)),
				'Frodo'
			),
			(
				'"{event.user_id}"',
				SensorDataEvent(-1, MagicMock(ScopedSession), Plant(name='Frodo'), SensorData(plant_id=-1, time=datetime.now(), temperature=70, humidity=40, soil_moisture=20, light=100_000)),
				'-1'
			),
			(
				{
					'name': '{event.plant.name}'
				},
				SensorDataEvent(-1, MagicMock(ScopedSession), Plant(name='Frodo'), SensorData(plant_id=-1, time=datetime.now(), temperature=70, humidity=40, soil_moisture=20, light=100_000)),
				{
					'name': 'Frodo'
				}
			),
			(
				['{event.plant.name}', 'foo', 12, '{event.data.temperature}'],
				SensorDataEvent(-1, MagicMock(ScopedSession), Plant(name='Frodo'), SensorData(plant_id=-1, time=datetime.now(), temperature=70, humidity=40, soil_moisture=20, light=100_000)),
				['Frodo', 'foo', 12, 70]
			),
			(
				12,
				SensorDataEvent(-1, MagicMock(ScopedSession), Plant(name='Frodo'), SensorData(plant_id=-1, time=datetime.now(), temperature=70, humidity=40, soil_moisture=20, light=100_000)),
				12
			),
			(
				None,
				SensorDataEvent(-1, MagicMock(ScopedSession), Plant(name='Frodo'), SensorData(plant_id=-1, time=datetime.now(), temperature=70, humidity=40, soil_moisture=20, light=100_000)),
				None
			),
		]
	)
	def test_template(self, value, event, expected):
		"""Test template produces the correct values"""
		action = HTTPAction('', '')
		message = action.template(value, event)
		assert message == expected

	@pytest.mark.parametrize('url, method, headers, params, body, event, expected', [
			(
				'http://foo.bar',
				'GET',
				None, None,
				None,
				SensorDataEvent(-1, MagicMock(ScopedSession), Plant(name='Frodo'), SensorData(plant_id=-1, time=datetime.now(), temperature=70, humidity=40, soil_moisture=20, light=100_000)),
				{}
			),
			(
				'http://foo.bar',
				'PATCH',
				{'user': '{event.user_id}'}, None,
				None,
				SensorDataEvent(-1, MagicMock(ScopedSession), Plant(name='Frodo'), SensorData(plant_id=-1, time=datetime.now(), temperature=70, humidity=40, soil_moisture=20, light=100_000)),
				{'headers': { 'user': -1 }}
			),
			(
				'http://foo.bar/{event.plant.plant_id}',
				'POST',
				None, None,
				'{event.plant.name}',
				SensorDataEvent(-1, MagicMock(ScopedSession), Plant(name='Frodo', plant_id=-1), SensorData(plant_id=-1, time=datetime.now(), temperature=70, humidity=40, soil_moisture=20, light=100_000)),
				{'url': 'http://foo.bar/-1', 'json': 'Frodo'}
			),
			(
				'http://foo.bar',
				'POST',
				{'Authorization': 'Bearer NotAToken'}, {'user': '{event.user_id}'},
				{
					'plant': '{event.plant.name}',
					'temperature': '{event.data.temperature}',
					'humidity': '{event.data.humidity}',
					'soil_moisture': '{event.data.soil_moisture}',
					'light': '{event.data.light}'
				},
				SensorDataEvent(-1, MagicMock(ScopedSession), Plant(name='Frodo', plant_id=-1), SensorData(plant_id=-1, time=datetime.now(), temperature=70, humidity=40, soil_moisture=20, light=100_000)),
				{
					'params': {
						'user': -1
					},
					'json': {
						'plant': 'Frodo',
						'temperature': 70,
						'humidity': 40,
						'soil_moisture': 20,
						'light': 100_000
					}
				}
			),
		]
	)
	@patch('requests.request')
	def test_execute(self, request_patch, url, headers, params, body, event, method, expected):
		action = HTTPAction(url, method, body, params, headers)

		action.execute(event)

		expected = {
			'url': url,
			'method': method,
			'params': params,
			'json': body,
			'headers': headers,
			**expected,
		}
		request_patch.assert_called_once_with(**expected, timeout=10)

	default_values = {
		'cooldown': None,
		'headers': None,
		'params': None,
		'body': None
	}
	@pytest.mark.parametrize('action, expected', [
		(HTTPAction('http://foo.bar', 'GET'), {
			**default_values,
			'url': 'http://foo.bar',
			'method': 'GET',
		}),
		(HTTPAction('http://foo.bar/{event.plant.plant_id}', 'POST', body='{event.user_id}'), {
			**default_values,
			'url': 'http://foo.bar/{event.plant.plant_id}',
			'method': 'POST',
			'body': {
				'str': '{event.user_id}'
			}
		}),
		(HTTPAction('http://foo.bar/{event.plant.plant_id}', 'POST', body={'user': '{event.user_id}'}), {
			**default_values,
			'url': 'http://foo.bar/{event.plant.plant_id}',
			'method': 'POST',
			'body': {
				'dict': {
					'user': '{event.user_id}'
				}
			}
		}),
		(HTTPAction('http://foo.bar', 'POST', headers={'Authorization': 'Bearer NotAToken'}, params={'user': '{event.user_id}'}), {
			**default_values,
			'url': 'http://foo.bar',
			'method': 'POST',
			'params': {
				'dict': {
					'user': '{event.user_id}'
				}
			},
			'headers': {
				'dict': {
					'Authorization': 'Bearer NotAToken'
				}
			}
		}),
	])
	def test_serialization(self, action, expected):
		res = HTTPActionSchema().dump(action)
		assert res == expected
		serialized = HTTPActionSchema().load(res)
		assert serialized == action
