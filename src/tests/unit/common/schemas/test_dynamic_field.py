from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from app.common.schemas import DynamicField, SerializableClass
from app.common.utils import PolymorphicSchema
from app.core.event_engine.post_process_functions import ValueRating
from marshmallow import fields, post_load, Schema, ValidationError
import pytest

class FooSchema(Schema):
	foo = DynamicField(allow_none=True)

	@post_load
	def make(self, data, **kwargs):
		return Foo(**data)

@dataclass
class Foo():
	foo: Any

class BazSchema(Schema):
	baz = DynamicField(allow_none=True)
@dataclass
class Baz(SerializableClass):
	__schema__ = BazSchema
	baz: Any

class Baz2Schema(BazSchema):
	bar = DynamicField()
@dataclass
class Baz2(Baz):
	__schema__ = Baz2Schema
	bar: Any

@dataclass
class UnregisteredClass:
	bar: int

@dataclass
class Bar:
	a: Any

class TestDynamicField:
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
		(Foo(foo=datetime(1, 1, 1, 1)), {
			'foo': {
				'value': '0001-01-01T01:00:00',
				'type': 'datetime'
			}
		}),
		(Foo(foo=ValueRating.High), {
			'foo': {
				'value': 'High',
				'type': 'ValueRating'
			}
		}),
	])
	def test_dump(self, value, expected):
		res = FooSchema().dump(value)
		assert res == expected

	@pytest.mark.parametrize('value', [
		(Foo(foo=UnregisteredClass(bar=2))),
	])
	def test_dump_raises(self, value):
		with pytest.raises(ValidationError):
			FooSchema().dump(value)

	@pytest.mark.parametrize('value, whitelist', [
		(Bar(a=3), [int]),
		(Bar(a=3), [int, float, str]),
		(Bar(a=ValueRating.High), [ValueRating]),
		(Bar(a=ValueRating.High), [int]),
		(Bar(a=Baz(baz=3)), [Baz]),
		(Bar(a=Baz2(baz=3, bar='foo')), [Baz]),
	])
	def test_dump_whitelist(self, value, whitelist):
		class BarSchema(Schema):
			a = DynamicField(whitelist)
		BarSchema().dump(value)

	@pytest.mark.parametrize('value, whitelist', [
		(Bar(a=5), [str]),
		(Bar(a='foo'), [int, float, datetime]),
		(Bar(a=ValueRating.High), [str]),
	])
	def test_dump_whitelist_raises(self, value, whitelist):
		class BarSchema(Schema):
			a = DynamicField(whitelist)

		with pytest.raises(ValidationError):
			BarSchema().dump(value)

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
		({
			'foo': {
				'value': '0001-01-01T01:00:00',
				'type': 'datetime'
			}
		}, Foo(foo=datetime(1, 1, 1, 1))),
		({
			'foo': {
				'value': 'High',
				'type': 'ValueRating'
			}
		}, Foo(foo=ValueRating.High)),
	])
	def test_load(self, value, expected):
		res = FooSchema().load(value)
		assert res == expected

	@pytest.mark.parametrize('value', [
		({
			'foo': {
				'value': 'bar',
				'type': 'BadType'
			}
		}),
		({
			'foo': {
				'type': 'int'
			}
		}),
		({
			'foo': {
				'value': 'MissingType'
			}
		}),
		({
			'foo': {
				'value': 'BadValue',
				'type': 'int'
			}
		}),
	])
	def test_load_raises(self, value):
		with pytest.raises(ValidationError):
			FooSchema().load(value)

	@pytest.mark.parametrize('value, whitelist', [
		({
			'a': {
				'value': 5,
				'type': 'int'
			}
		}, [int]),
		({
			'a': {
				'value': 5,
				'type': 'int'
			}
		}, [int, float, str]),
		({
			'a': {
				'value': 'High',
				'type': 'ValueRating'
			}
		}, [ValueRating]),
		({
			'a': {
				'value': 'High',
				'type': 'ValueRating'
			}
		}, [int]),
		({
			'a': {
				'value': {
					'baz': {
						'value': 5,
						'type': 'int'
					}
				},
				'type': 'Baz'
			}
		}, [Baz]),
		({
			'a': {
				'value': {
					'baz': {
						'value': 5,
						'type': 'int'
					},
					'bar': {
						'value': 5,
						'type': 'int'
					}
				},
				'type': 'Baz2'
			}
		}, [Baz]),
	])
	def test_load_whitelist(self, value, whitelist):
		class BarSchema(Schema):
			a = DynamicField(whitelist)
		BarSchema().load(value)

	@pytest.mark.parametrize('value, whitelist', [
		({
			'a': {
				'value': 5,
				'type': 'int'
			}
		}, [str]),
		({
			'a': {
				'value': 'foo',
				'type': 'str'
			}
		}, [int, float, datetime]),
		({
			'a': {
				'value': 'High',
				'type': 'ValueRating'
			}
		}, [str]),
	])
	def test_load_whitelist_raises(self, value, whitelist):
		class BarSchema(Schema):
			a = DynamicField(whitelist)

		with pytest.raises(ValidationError):
			BarSchema().load(value)