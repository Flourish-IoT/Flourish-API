from app.core.event_engine.events import Event
from app.core.event_engine.triggers import Trigger
from unittest.mock import MagicMock
import pytest

class ConcreteTrigger(Trigger):
	"""For testing only"""
	def execute(self, value, event: Event) -> bool:
		return True

# TODO: test get_actions
class TestTrigger:
	@pytest.mark.parametrize('value, expected, field', [
		(2, 2, None),
		( {'foo': 8}, 8, 'foo'),
		( {'foo': 2, 'bar': 20}, 20, 'bar')
	])
	def test_get_value(self, value, field, expected):
		"""Assert get_value returns the correct value"""
		trigger = ConcreteTrigger([], field)

		val = trigger.get_value(value)

		assert val == expected