from dataclasses import dataclass
from datetime import timedelta
from app.common.utils import PolymorphicSchema
from marshmallow import fields, post_load
import pytest
from app.common.utils.polymorphic_schema import PolymorphicSchemaLoader

from app.core.util import Serializable

class FooSchema(PolymorphicSchema):
	foo = fields.Bool()
	bar = fields.Int()

	@post_load
	def make(self, data, **kwargs):
		return Foo(**data)

class BarSchema(PolymorphicSchema):
	baz = fields.Email()
	aaa = fields.Float()

	@post_load
	def make(self, data, **kwargs):
		return Bar(**data)

class BazSchema(PolymorphicSchema):
	foo = fields.Nested(FooSchema)
	bar = fields.Nested(BarSchema)

	@post_load
	def make(self, data, **kwargs):
		return Baz(**data)

@dataclass
class Foo(Serializable):
	__schema__ = FooSchema
	foo: bool
	bar: int

@dataclass
class Bar(Serializable):
	__schema__ = BarSchema
	baz: str
	aaa: float

@dataclass
class Baz(Serializable):
	__schema__ = BazSchema
	foo: Foo
	bar: Bar

class TestActionInformation:
	@pytest.mark.parametrize('data, schema, expected', [
		(Foo(True, 5), FooSchema, {
			'foo': True,
			'bar': 5,
			'__schema__': {
				'__class__': 'FooSchema',
				'__module__': 'tests.unit.common.test_polymorphic_schema'
			}
		}),
		(Bar('foo@bar.com', 2.3), BarSchema, {
			'baz': 'foo@bar.com',
			'aaa': 2.3,
			'__schema__': {
				'__class__': 'BarSchema',
				'__module__': 'tests.unit.common.test_polymorphic_schema'
			}
		}),
		(Baz(Foo(True, 5), Bar('foo@bar.com', 2.3)), BazSchema, {
			'foo': {
				'foo': True,
				'bar': 5,
				'__schema__': {
					'__class__': 'FooSchema',
					'__module__': 'tests.unit.common.test_polymorphic_schema'
				}
			},
			'bar': {
				'baz': 'foo@bar.com',
				'aaa': 2.3,
				'__schema__': {
					'__class__': 'BarSchema',
					'__module__': 'tests.unit.common.test_polymorphic_schema'
				}
			},
			'__schema__': {
				'__class__': 'BazSchema',
				'__module__': 'tests.unit.common.test_polymorphic_schema'
			}
		}),
	])
	def test_dump(self, data, schema, expected):
		"""Ensure polymorphic schema is dumped correctly"""
		obj = schema().dump(data)

		assert obj == expected

	@pytest.mark.parametrize('data, expected, expected_cls', [
		({
			'foo': True,
			'bar': 5,
			'__schema__': {
				'__class__': 'FooSchema',
				'__module__': 'tests.unit.common.test_polymorphic_schema'
			}
		}, Foo(True, 5), Foo),
		({
			'baz': 'foo@gmail.com',
			'aaa': 2.3,
			'__schema__': {
				'__class__': 'BarSchema',
				'__module__': 'tests.unit.common.test_polymorphic_schema'
			}
		}, Bar('foo@gmail.com', 2.3), Bar),
		({
			'foo': {
				'foo': True,
				'bar': 5,
				'__schema__': {
					'__class__': 'FooSchema',
					'__module__': 'tests.unit.common.test_polymorphic_schema'
				}
			},
			'bar': {
				'baz': 'foo@bar.com',
				'aaa': 2.3,
				'__schema__': {
					'__class__': 'BarSchema',
					'__module__': 'tests.unit.common.test_polymorphic_schema'
				}
			},
			'__schema__': {
				'__class__': 'BazSchema',
				'__module__': 'tests.unit.common.test_polymorphic_schema'
			}
		}, Baz(Foo(True, 5), Bar('foo@bar.com', 2.3)), Baz)
	])
	def test_load(self, data, expected, expected_cls):
		"""Ensure polymorphic schema is loaded correctly"""
		cls = PolymorphicSchemaLoader().load(data)

		assert cls == expected
		assert type(cls) == expected_cls