from datetime import timedelta
from app.core.event_engine.events.triggers.actions import Action
import pytest

class ConcreteAction(Action):
	"""For testing only"""
	def execute(self, event):
		pass

class TestAction:
	@pytest.mark.parametrize('disabled, cooldown, can_execute', [
			(False, None, True),
			(True, None, False),
		]
	)
	# TODO: test cooldown
	def test_can_execute(self, disabled, cooldown, can_execute):
		"""Test if can_execute correctly determines whether action can execute or not"""
		action = ConcreteAction(disabled, cooldown)
		assert action.can_execute() == can_execute