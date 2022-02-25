from app.core.event_engine.events import Event
from app.core.event_engine.events.triggers import AndTrigger
from unittest.mock import MagicMock
import pytest

from app.core.event_engine.events.triggers import Trigger

class TestAnd:
	def test_execute(self):
		"""Assert trigger only executes when both triggers return true"""
		value = 5

		mock_action = MagicMock()
		mock_action_2 = MagicMock()

		mock_trigger = MagicMock(Trigger)
		mock_trigger_2 = MagicMock(Trigger)

		mock_trigger.execute.return_value = True
		mock_trigger_2.execute.return_value = True

		mock_event = MagicMock(Event)
		trigger = AndTrigger([mock_trigger, mock_trigger_2], [mock_action, mock_action_2])

		executed = trigger.execute(value, mock_event)

		mock_action.execute.assert_called_once_with(mock_event)
		mock_action_2.execute.assert_called_once_with(mock_event)

		mock_trigger.execute.assert_called_once_with(value, mock_event)
		mock_trigger_2.execute.assert_called_once_with(value, mock_event)

		assert executed == True

	@pytest.mark.parametrize('trigger_1_succeeds, trigger_2_succeeds', [ (True, False), (False, True), ])
	def test_no_execute(self, trigger_1_succeeds, trigger_2_succeeds):
		"""Assert trigger does not execute if one trigger fails"""
		value = 5

		mock_action = MagicMock()
		mock_action_2 = MagicMock()

		mock_trigger = MagicMock(Trigger)
		mock_trigger_2 = MagicMock(Trigger)

		mock_trigger.execute.return_value = trigger_1_succeeds
		mock_trigger_2.execute.return_value = trigger_2_succeeds

		mock_event = MagicMock(Event)
		trigger = AndTrigger([mock_trigger, mock_trigger_2], [mock_action, mock_action_2])

		executed = trigger.execute(value, mock_event)

		mock_action.execute.assert_not_called()
		mock_action_2.execute.assert_not_called()

		assert executed == False