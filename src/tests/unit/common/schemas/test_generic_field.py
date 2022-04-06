from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from app.common.schemas.generic_field import GenericField
from app.common.utils import PolymorphicSchema, Serializable
from app.core.event_engine.post_process_functions import ValueRating
from marshmallow import fields, post_load, Schema
import pytest

class FooSchema(Schema):
	foo = GenericField()

	@post_load
	def make(self, data, **kwargs):
		return Foo(**data)

@dataclass
class Foo():
	foo: Any

class TestAnyField:
	@pytest.mark.parametrize('value, expected', [
		(Foo(foo=5), {
			'foo': {
				'value': 5,
				'type': 'int'
			}
		}),
		(Foo(foo=2.3), {
			'foo': {
				'value': 2.3,
				'type': 'float'
			}
		}),
		(Foo(foo=float(2)), {
			'foo': {
				'value': 2.0,
				'type': 'float'
			}
		}),
		(Foo(foo=None), {
			'foo': {
				'value': None,
				'type': 'NoneType'
			}
		}),
		(Foo(foo='abc'), {
			'foo': {
				'value': 'abc',
				'type': 'str'
			}
		}),
		# (Foo(foo=datetime(1, 1, 1, 1)), {
		# 	'foo': {
		# 		'value': None,
		# 		'type': 'datetime.datetime'
		# 	}
		# }),
		(Foo(foo=ValueRating.High), {
			'foo': {
				'value': 4,
				'type': 'app.core.event_engine.post_process_functions.target_value_score.ValueRating'
			}
		}),
	])
	def test_dump(self, value, expected):
		res = FooSchema().dump(value)
		assert res == expected

	@pytest.mark.parametrize('value, expected', [
		({
			'foo': {
				'value': 5,
				'type': 'int'
			}
		}, Foo(foo=5)),
		({
			'foo': {
				'value': 2.3,
				'type': 'float'
			}
		}, Foo(foo=2.3)),
		({
			'foo': {
				'value': 2.0,
				'type': 'float'
			}
		}, Foo(foo=float(2))),
		({
			'foo': {
				'value': None,
				'type': 'NoneType'
			}
		}, Foo(foo=None)),
		({
			'foo': {
				'value': 'abc',
				'type': 'str'
			}
		}, Foo(foo='abc')),
		# (Foo(foo=datetime(1, 1, 1, 1)), {
		# 	'foo': {
		# 		'value': None,
		# 		'type': 'datetime.datetime'
		# 	}
		# }),
		({
			'foo': {
				'value': 4,
				'type': 'app.core.event_engine.post_process_functions.target_value_score.ValueRating'
			}
		}, Foo(foo=ValueRating.High)),
	])
	def test_load(self, value, expected):
		res = FooSchema().load(value)
		assert res == expected
