from datetime import timedelta
from app.core.event_engine.actions import Action, ActionSchema, GenerateAlertAction
from unittest.mock import MagicMock
import pytest

from app.core.models.event_engine import ActionInformation
from app.core.models import SeverityLevelEnum
from marshmallow import post_load

class ConcreteActionSchema(ActionSchema):
	@post_load
	def make(self, data, **kwargs):
		return ConcreteAction(**data, **self.context)

class ConcreteAction(Action):
	__schema__ = ConcreteActionSchema

	"""For testing only"""
	def execute(self, event) -> bool:
			return super().execute(event)

class TestActionInformation:
	@pytest.mark.parametrize('action, expected', [
		(ConcreteAction(False, action_id=-1, cooldown=timedelta(days=3)), ActionInformation(action_id=-1, disabled = False, last_executed = None, action={
			'type': 'ConcreteAction',
			'cooldown': 259200,
		})),
		(GenerateAlertAction('{foo} bar', SeverityLevelEnum.Critical, False, action_id=-1, cooldown=timedelta(days=3)), ActionInformation(action_id=-1, disabled = False, last_executed = None, action={
			'type': 'GenerateAlertAction',
			'message_template': '{foo} bar',
			'severity': 'Critical',
			'cooldown': 259200,
		}))
	])
	def test_from_action(self, action, expected):
		"""Ensure action is properly created from an Action instance"""
		action_info = ActionInformation.from_action(action)
		expected._action = action

		assert action_info == expected
		assert action_info.action == expected.action

	@pytest.mark.parametrize('action_info, expected, expected_type', [
		(ActionInformation(action_id=-1, last_executed=None, disabled=False, action={
			'type': 'ConcreteAction',
			'cooldown': 259200,
		}), ConcreteAction(False, action_id=-1, cooldown=timedelta(days=3)), ConcreteAction),
		(ActionInformation(action_id=-1, disabled=True, last_executed=None, action={
			'type': 'GenerateAlertAction',
			'message_template': '{foo} bar',
			'severity': 'Critical',
			'cooldown': 259200,

		}), GenerateAlertAction('{foo} bar', SeverityLevelEnum.Critical, True, action_id=-1, cooldown=timedelta(days=3)), GenerateAlertAction)
	])
	def test_to_action(self, action_info: ActionInformation, expected, expected_type):
		"""Ensure action is properly created from an Action instance"""
		action = action_info.to_action()

		assert action.__dict__ == expected.__dict__
		assert type(action) == expected_type

	# def test_to_action(self):
	# 	"""Ensure action is properly created from an ActionInformation instance"""


	# def test_from_to_action(self):
	# 	"""Ensure from_action generates json that can be loaded by to_action"""
		# action = GenerateAlertAction('Foo', SeverityLevelEnum.Info, False)
		# # action = ConcreteAction(False)
		# # action = ConcreteAction(False, cooldown=timedelta(days=3))
		# action_info = ActionInformation.from_action(action)
		# loaded_action = action_info.to_action()
		# print(loaded_action)