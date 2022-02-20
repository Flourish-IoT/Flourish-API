from app.core.event_engine.events.triggers import EqualsTrigger
from app.core.event_engine.events.field.score_functions import ValueRating
from unittest.mock import MagicMock
import pytest

class TestEquals:
	@pytest.mark.parametrize('value', [2, ValueRating.Nominal])
	def test_execute(self, value):
		"""Assert trigger only executes on the right value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		trigger = EqualsTrigger([mock_action, mock_action_2], value)

		executed = trigger.execute(value)
		mock_action.execute.assert_called_once()
		mock_action_2.execute.assert_called_once()
		assert executed == True

	@pytest.mark.parametrize('value_1, value_2', [( 2, 3 ), ( ValueRating.Nominal, ValueRating.TooHigh )])
	def test_no_execute(self, value_1, value_2):
		"""Assert trigger does not execute on the wrong value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		trigger = EqualsTrigger([mock_action, mock_action_2], value_1)

		executed = trigger.execute(value_2)
		mock_action.execute.assert_not_called()
		mock_action_2.execute.assert_not_called()
		assert executed == False