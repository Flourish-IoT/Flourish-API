from app.core.event_engine.events import Event
from app.core.event_engine.triggers import GreaterThanTrigger
from app.core.event_engine.post_process_functions import ValueRating
from unittest.mock import MagicMock
import pytest

class TestGreaterThan:
	@pytest.mark.parametrize('value, gt_value, field', [
		( 2, 1, None ), (1.5, 1.4, None), (ValueRating.High, ValueRating.Nominal, None),
		( {'foo': 2}, 1, 'foo' ), ({'foo': 4, 'bar': 20}, 18, 'bar'),
	])
	def test_execute(self, value, gt_value, field):
		"""Assert trigger only executes on the right value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		mock_event = MagicMock(Event)
		trigger = GreaterThanTrigger(gt_value, [mock_action, mock_action_2], field=field)

		executed = trigger.execute(value, mock_event)
		mock_action.execute.assert_called_once_with(mock_event)
		mock_action_2.execute.assert_called_once_with(mock_event)
		assert executed == True

	@pytest.mark.parametrize('value, gt_value, field', [
		( 1, 2, None ), (1.4, 1.5, None), (ValueRating.Low, ValueRating.Nominal, None),
		( {'foo': 1}, 2, 'foo' ), ({'foo': 50, 'bar': 9}, 18, 'bar'),
	])
	def test_no_execute(self, value, gt_value, field):
		"""Assert trigger does not execute on the wrong value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		mock_event = MagicMock(Event)
		trigger = GreaterThanTrigger(gt_value, [mock_action, mock_action_2], field=field)

		executed = trigger.execute(value, mock_event)
		mock_action.execute.assert_not_called()
		mock_action_2.execute.assert_not_called()
		assert executed == False