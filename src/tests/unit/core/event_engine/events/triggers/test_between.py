from app.core.event_engine.events.triggers import BetweenTrigger
from app.core.event_engine.events.field.score_functions import ValueRating
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


	@pytest.mark.parametrize('min, max, value', [( 1, 3, 2 ), (1.2, 1.4, 1.3), (ValueRating.TooLow, ValueRating.Nominal, ValueRating.Low)])
	def test_execute(self, min, max, value):
		"""Assert trigger only executes on the right value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		trigger = BetweenTrigger(min, max, [mock_action, mock_action_2])

		executed = trigger.execute(value)
		mock_action.execute.assert_called_once()
		mock_action_2.execute.assert_called_once()
		assert executed == True

	@pytest.mark.parametrize('min, max, value', [( 1, 3, 4 ), (1.2, 1.4, 1.0), ( ValueRating.Nominal, ValueRating.TooHigh, ValueRating.Low )])
	def test_no_execute(self, min, max, value):
		"""Assert trigger does not execute on the wrong value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		trigger = BetweenTrigger(min, max, [mock_action, mock_action_2])

		executed = trigger.execute(value)
		mock_action.execute.assert_not_called()
		mock_action_2.execute.assert_not_called()
		assert executed == False