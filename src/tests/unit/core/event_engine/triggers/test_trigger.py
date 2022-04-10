from app.common.schemas.dynamic_schema import DynamicSchema
from app.core.event_engine.events import Event
from app.core.event_engine.triggers import Trigger, TriggerSchema
from unittest.mock import MagicMock
from marshmallow import post_load
import pytest

from tests.unit.core.event_engine.actions.test_action import ConcreteAction

class ConcreteTriggerSchema(TriggerSchema):
	@post_load
	def make(self, data, **kwargs):
		return ConcreteTrigger(**data)

class ConcreteTrigger(Trigger):
	__schema__ = ConcreteTriggerSchema
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

	@pytest.mark.parametrize('trigger, expected', [
		(ConcreteTrigger([], 'foo'), {
			'type': 'ConcreteTrigger',
			'actions': [],
			'field': 'foo'
		}),
		(ConcreteTrigger([ConcreteAction(action_id=-1, disabled=False)]), {
			'type': 'ConcreteTrigger',
			'actions': [-1],
			'field': None
		}),
		(ConcreteTrigger([ConcreteAction(action_id=-1, disabled=False), ConcreteAction(action_id=-2, disabled=True)], 'foo'), {
			'type': 'ConcreteTrigger',
			'actions': [-1, -2],
			'field': 'foo'
		}),
	])
	def test_serialization(self, trigger, expected):
		res = DynamicSchema().dump(trigger)
		assert res == expected

	@pytest.mark.parametrize('data, context, expected', [
		({
			'type': 'ConcreteTrigger',
			'actions': [],
			'field': 'foo'
		}, {'action_map': {}}, ConcreteTrigger([], 'foo')),
		({
			'type': 'ConcreteTrigger',
			'actions': [],
			'field': None,
		}, {'action_map': {-1: ConcreteAction(action_id=-1, disabled=False)} }, ConcreteTrigger([])),
		({
			'type': 'ConcreteTrigger',
			'actions': [-1],
			'field': 'foo'
		}, {'action_map': {-1: ConcreteAction(action_id=-1, disabled=False)} }, ConcreteTrigger([ConcreteAction(action_id=-1, disabled=False)], 'foo')),
		({
			'type': 'ConcreteTrigger',
			'actions': [-1, -2],
			'field': 'foo'
		}, {'action_map': {-1: ConcreteAction(action_id=-1, disabled=False), -2: ConcreteAction(action_id=-2, disabled=True)} }, ConcreteTrigger([ConcreteAction(action_id=-1, disabled=False), ConcreteAction(action_id=-2, disabled=True)], 'foo')),
	])
	def test_deserialization(self, data, context, expected):
		schema = DynamicSchema()
		schema.context = context
		res = schema.load(data)
		assert res == expected