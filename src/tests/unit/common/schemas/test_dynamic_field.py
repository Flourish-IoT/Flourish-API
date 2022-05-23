from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from app.common.schemas import DynamicField, SerializableClass
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

# for testing context
class ContextTestSchema(Schema):
	func = fields.Function(lambda _, ctx: ctx, lambda _, ctx: ctx)

@dataclass
class ContextTest(SerializableClass):
	__schema__ = ContextTestSchema
	func: Any

class TestDynamicField:
	@pytest.mark.parametrize('value, expected', [
		(Foo(foo=5), {
			'foo': {
				'int': 5
			}
		}),
		(Foo(foo=2.3), {
			'foo': {
				'float': 2.3
			}
		}),
		(Foo(foo=float(2)), {
			'foo': {
				'float': 2
			}
		}),
		(Foo(foo=None), {
			'foo': None
		}),
		(Foo(foo='abc'), {
			'foo': {
				'str': 'abc'
			}
		}),
		(Foo(foo=datetime(1, 1, 1, 1)), {
			'foo': {
				'datetime': '0001-01-01T01:00:00',
			}
		}),
		(Foo(foo=ValueRating.High), {
			'foo': {
				'ValueRating': 'High',
			}
		}),
		(Foo(foo={'foo': 'bar'}), {
			'foo': {
				'dict': {
					'foo': 'bar'
				},
			}
		}),
		(Foo(foo={'foo': {'bar': 12}}), {
			'foo': {
				'dict': {
					'foo': {
						'bar': 12
					}
				},
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

	def test_dump_allow_none(self):
		class AllowNoneSchema(Schema):
			a = DynamicField(allow_none=True)
		class DontAllowNoneSchema(Schema):
			a = DynamicField(allow_none=False)

		@dataclass
		class Container():
			a: Any

		AllowNoneSchema().dump(Container(a=None))
		with pytest.raises(ValidationError):
			DontAllowNoneSchema().dump(Container(a=None))

	def test_dump_context(self):
		context = {'context_test': 3}
		res = FooSchema(context=context).dump(Foo(ContextTest('GETS OVERRIDEN')))
		assert res == {
			'foo': {
				'ContextTest': {
					'func': {
						'context_test': 3
					}
				}
			}
		}

	@pytest.mark.parametrize('value, expected', [
		({
			'foo': {
				'int': 5
			}
		}, Foo(foo=5)),
		({
			'foo': {
				'float': 2.3,
			}
		}, Foo(foo=2.3)),
		({
			'foo': {
				'float': 2.0,
			}
		}, Foo(foo=float(2))),
		({
			'foo': None
		}, Foo(foo=None)),
		({
			'foo': {
				'str': 'abc',
			}
		}, Foo(foo='abc')),
		({
			'foo': {
				'datetime': '0001-01-01T01:00:00',
			}
		}, Foo(foo=datetime(1, 1, 1, 1))),
		({
			'foo': {
				'ValueRating': 'High',
			}
		}, Foo(foo=ValueRating.High)),
		({
			'foo': {
				'dict': {
					'foo': 'bar'
				}
			}
		}, Foo(foo={'foo': 'bar'})),
		({
			'foo': {
				'dict': {
					'foo': {
						'bar': 12
					}
				}
			}
		}, Foo(foo={'foo': {'bar': 12}})),
	])
	def test_load(self, value, expected):
		res = FooSchema().load(value)
		assert res == expected

	@pytest.mark.parametrize('value', [
		({
			'foo': {
				'BadType': 'bar',
			}
		}),
		({
			'foo': {
				'': 'MissingType'
			}
		}),
		({
			'foo': {
				'int': 'BadValue',
			}
		}),
	])
	def test_load_raises(self, value):
		with pytest.raises(ValidationError):
			FooSchema().load(value)

	@pytest.mark.parametrize('value, whitelist', [
		({
			'a': {
				'int': 5,
			}
		}, [int]),
		({
			'a': {
				'int': 5,
			}
		}, [int, float, str]),
		({
			'a': {
				'ValueRating': 'High',
			}
		}, [ValueRating]),
		({
			'a': {
				'ValueRating': 'High',
			}
		}, [int]),
		({
			'a': {
				'Baz': {
					'baz': {
						'int': 5,
					}
				},
			}
		}, [Baz]),
		({
			'a': {
				'Baz2': {
					'baz': {
						'int': 5,
					},
					'bar': {
						'int': 5,
					}
				},
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
				'int': 5,
			}
		}, [str]),
		({
			'a': {
				'str': 'foo',
			}
		}, [int, float, datetime]),
		({
			'a': {
				'ValueRating': 'High',
			}
		}, [str]),
	])
	def test_load_whitelist_raises(self, value, whitelist):
		class BarSchema(Schema):
			a = DynamicField(whitelist)

		with pytest.raises(ValidationError):
			BarSchema().load(value)

	def test_load_allow_none(self):
		class AllowNoneSchema(Schema):
			a = DynamicField(allow_none=True)
		class DontAllowNoneSchema(Schema):
			a = DynamicField(allow_none=False)

		AllowNoneSchema().load({'a': None})
		with pytest.raises(ValidationError):
			DontAllowNoneSchema().dump({'a': None})

	def test_load_context(self):
		context = {'context_test': 3}

		res = FooSchema(context=context).load({
			'foo': {
				'ContextTest': {
					'func': 'GETS OVERRIDEN'
				}
			}
		})

		assert res == Foo({
			'func': {
				'context_test': 3
			}
		})