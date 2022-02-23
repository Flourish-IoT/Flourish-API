from datetime import timedelta
from app.core.event_engine.events.events import SensorDataEvent
import pytest

from app.core.event_engine.events.triggers.actions import GenerateAlertAction
from app.core.models import SeverityLevelEnum, Plant, SensorData

class TestGenerateAlertAction:
	@pytest.mark.parametrize('template, data, plant, expected', [
			('{event.plant.name}', None,  Plant(name='Foo'), 'Foo'),
			('{event.plant.name} has temperature {event.data.temperature} degrees', SensorData(temperature=90), Plant(name='Bar'), 'Bar has temperature 90 degrees'),
		]
	)
	# TODO: expand?
	# TODO: Add DeviceUpdate event
	def test_generate_message(self, template, plant, data, expected):
		"""Test generate_message produces the correct message"""
		action = GenerateAlertAction(template, SeverityLevelEnum.Info, False)
		message = action.generate_message(SensorDataEvent(plant=plant, data=data))
		assert message == expected

	# TODO: test persistance