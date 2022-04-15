from datetime import timedelta, datetime
from app.core.event_engine.actions import Action
import pytest

class ConcreteAction(Action):
	"""For testing only"""
	def execute(self, event):
		pass

class TestAction:
	@pytest.mark.parametrize('disabled, cooldown, last_executed, can_execute', [
			(False, None, None, True),
			(True, None, None, False),
			(False, timedelta(days=1), datetime.now() - timedelta(days=2), True),
			(False, timedelta(days=1), datetime.now(), False),
		]
	)
	# TODO: test cooldown
	def test_can_execute(self, disabled, cooldown, last_executed, can_execute):
		"""Test if can_execute correctly determines whether action can execute or not"""
		action = ConcreteAction(disabled, cooldown=cooldown, last_executed=last_executed)
		assert action.can_execute() == can_execute