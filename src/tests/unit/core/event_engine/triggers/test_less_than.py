from app.common.schemas import DynamicSchema
from app.core.event_engine.actions.action import Action
from app.core.event_engine.events import Event
from app.core.event_engine.triggers import LessThanTrigger
from app.core.event_engine.post_process_functions import ValueRating
from unittest.mock import MagicMock
import pytest

class TestLessThan:
	@pytest.mark.parametrize('value, lt_value, field', [
		( 1, 2, None ), (1.4, 1.5, None), (ValueRating.Low, ValueRating.Nominal, None),
		( {'foo': 1}, 2, 'foo' ), ({'foo': 50, 'bar': 9}, 18, 'bar'),
	])
	def test_execute(self, value, lt_value, field):
		"""Assert trigger only executes on the right value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		mock_event = MagicMock(Event)
		trigger = LessThanTrigger(lt_value, [mock_action, mock_action_2], field=field)

		executed = trigger.execute(value, mock_event)
		mock_action.execute.assert_called_once_with(mock_event)
		mock_action_2.execute.assert_called_once_with(mock_event)
		assert executed == True

	@pytest.mark.parametrize('value, lt_value, field', [
		( 2, 1, None ), (1.5, 1.4, None), (ValueRating.High, ValueRating.Nominal, None),
		( {'foo': 2}, 1, 'foo' ), ({'foo': 4, 'bar': 20}, 18, 'bar'),
	])
	def test_no_execute(self, value, lt_value, field):
		"""Assert trigger does not execute on the wrong value"""
		mock_action = MagicMock()
		mock_action_2 = MagicMock()
		mock_event = MagicMock(Event)
		trigger = LessThanTrigger(lt_value, [mock_action, mock_action_2], field=field)

		executed = trigger.execute(value, mock_event)
		mock_action.execute.assert_not_called()
		mock_action_2.execute.assert_not_called()
		assert executed == False

	@pytest.mark.parametrize('trigger, expected', [
		(LessThanTrigger(2, [], field='foo'), {
			'type': 'LessThanTrigger',
			'value': {
				'value': 2,
				'type': 'int'
			},
			'actions': [],
			'field': 'foo'
		}),
		(LessThanTrigger(2.4, [MagicMock(Action, action_id=-1)], field='foo'), {
			'type': 'LessThanTrigger',
			'value': {
				'value': 2.4,
				'type': 'float'
			},
			'actions': [-1],
			'field': 'foo'
		}),
		(LessThanTrigger(ValueRating.High, [MagicMock(Action, action_id=-1, disabled=False), MagicMock(Action, action_id=-2, disabled=True)]), {
			'type': 'LessThanTrigger',
			'actions': [-1, -2],
			'value': {
				'value': 4,
				'type': 'app.core.event_engine.post_process_functions.target_value_score.ValueRating'
			},
			'field': None
		}),
	])
	def test_serialization(self, trigger, expected):
		res = DynamicSchema().dump(trigger)
		assert res == expected

	@pytest.mark.parametrize('data, context, expected', [
		({
			'type': 'LessThanTrigger',
			'value': {
				'value': 2.0,
				'type': 'float'
			},
			'actions': [],
			'field': 'foo'
		}, {'action_map': {}}, LessThanTrigger(2.0, [], field='foo')),
		({
			'type': 'LessThanTrigger',
			'value': {
				'value': 2.4,
				'type': 'float'
			},
			'actions': [],
			'field': 'foo'
		}, {'action_map': {} }, LessThanTrigger(2.4, [], field='foo')),
		({
			'type': 'LessThanTrigger',
			'actions': [],
			'field': None,
			'value': {
				'value': -8,
				'type': 'int'
			},
		}, {'action_map': {} }, LessThanTrigger(-8, [])),
		({
			'type': 'LessThanTrigger',
			'actions': [],
			'field': 'foo',
			'value': {
				'value': 5,
				'type': 'app.core.event_engine.post_process_functions.target_value_score.ValueRating'
			},
		}, {'action_map': {} }, LessThanTrigger(ValueRating.TooHigh, [], field='foo')),
	])
	def test_deserialization(self, data, context, expected):
		schema = DynamicSchema()
		schema.context = context
		res = schema.load(data)
		assert res == expected