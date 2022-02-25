from app.core.event_engine.events.event import Event
from app.core.event_engine.triggers import EqualsTrigger
from app.core.event_engine.post_process_functions import ValueRating
from unittest.mock import MagicMock
import pytest

class TestEquals:
	@pytest.mark.parametrize('value, eq_value, field', [
		( 2, 2, None ), ( ValueRating.Nominal, ValueRating.Nominal, None ),
		( {'foo': 8.2}, 8.2, 'foo' ), ( { 'foo': ValueRating.Nominal, 'bar': 20}, ValueRating.Nominal, 'foo' )
		])
	def test_execute(self, value, eq_value, field):
		"""Assert trigger only executes on the right value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		mock_event = MagicMock(Event)
		trigger = EqualsTrigger(eq_value, [mock_action, mock_action_2], field=field)

		executed = trigger.execute(value, mock_event)
		mock_action.execute.assert_called_once_with(mock_event)
		mock_action_2.execute.assert_called_once_with(mock_event)
		assert executed == True

	@pytest.mark.parametrize('eq_value, value, field', [
		( 2, 3, None ), ( ValueRating.Nominal, ValueRating.TooHigh, None ),
		( 20, {'foo': 8}, 'foo' ), ( 40, { 'foo': ValueRating.Nominal, 'bar': 20}, 'foo' )
	])
	def test_no_execute(self, eq_value, value, field):
		"""Assert trigger does not execute on the wrong value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		mock_event = MagicMock(Event)
		trigger = EqualsTrigger(eq_value, [mock_action, mock_action_2], field=field)

		executed = trigger.execute(value, mock_event)
		mock_action.execute.assert_not_called()
		mock_action_2.execute.assert_not_called()
		assert executed == False