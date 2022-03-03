from app.core.event_engine.events import Event
from app.core.event_engine.triggers import BetweenTrigger
from app.core.event_engine.post_process_functions import ValueRating
from unittest.mock import MagicMock
import pytest

class TestBetween:
	@pytest.mark.parametrize('min, max', [(3, 1), (2, -2), (ValueRating.High, ValueRating.Low)])
	def test_ctor(self, min, max):
		"""Assert trigger constructor properly raises exceptions"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()

		with pytest.raises(ValueError):
			trigger = BetweenTrigger(min, max, [mock_action, mock_action_2])


	@pytest.mark.parametrize('min, max, value, field', [
		( 1, 3, 2, None ),
		(1.2, 1.4, 1.3, None),
		(ValueRating.TooLow, ValueRating.Nominal, ValueRating.Low, None),
		( 1, 3, {'foo': 2}, 'foo'),
		( 1, 3, {'foo': 8, 'bar': 2}, 'bar')
	])
	def test_execute(self, min, max, value, field):
		"""Assert trigger only executes on the right value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		mock_event = MagicMock(Event)
		trigger = BetweenTrigger(min, max, [mock_action, mock_action_2], field=field)

		executed = trigger.execute(value, mock_event)
		mock_action.execute.assert_called_once_with(mock_event)
		mock_action_2.execute.assert_called_once_with(mock_event)
		assert executed == True

	@pytest.mark.parametrize('min, max, value, field', [
		( 1, 3, 4, None ),
		(1.2, 1.4, 1.0, None),
		( ValueRating.Nominal, ValueRating.TooHigh, ValueRating.Low, None ),
		( 1, 3, {'foo': 8}, 'foo'),
		( 1, 3, {'foo': 2, 'bar': 20}, 'bar')
	])
	def test_no_execute(self, min, max, value, field):
		"""Assert trigger does not execute on the wrong value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		mock_event = MagicMock(Event)
		trigger = BetweenTrigger(min, max, [mock_action, mock_action_2], field=field)

		executed = trigger.execute(value, mock_event)
		mock_action.execute.assert_not_called()
		mock_action_2.execute.assert_not_called()
		assert executed == False