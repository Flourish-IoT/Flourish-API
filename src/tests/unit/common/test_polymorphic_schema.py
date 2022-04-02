from dataclasses import dataclass
from datetime import timedelta
from app.common.utils import PolymorphicSchema, Serializable
from marshmallow import fields, post_load, Schema
import pytest

class FooSchema(Schema):
	foo = fields.Bool()
	bar = fields.Int()

	@post_load
	def make(self, data, **kwargs):
		return Foo(**data)

@dataclass
class Foo():
	# used for testing manual registration
	__schema__ = FooSchema
	foo: bool
	bar: int

def restore_schema(func):
	"""Decorator to restore the PolymorphicSchema to previous state after test completes"""
	def f(*args, **kwargs):
		prev_schema = PolymorphicSchema.type_schemas
		try:
			r = func(*args, **kwargs)
		finally:
			PolymorphicSchema.type_schemas = prev_schema
		return r
	return f

class TestPolymorphicSchema:
	@restore_schema
	def test_register(self):
		"""Ensure polymorphic schema is registering correctly"""
		PolymorphicSchema.type_schemas = {}
		PolymorphicSchema.register(Foo, Foo.__schema__)

		assert PolymorphicSchema.type_schemas == {
			'Foo': FooSchema
		}

	# def test_multiple_register(self):
	# 	"""Ensure polymorphic schema throws an error when two classes with the same name have been registered"""
	# 	PolymorphicSchema.type_schemas = {}

	# 	PolymorphicSchema.register(Foo, Foo.__schema__)
	# 	with pytest.raises(ValueError):
	# 		PolymorphicSchema.register(Foo, Foo.__schema__)

	# 	assert PolymorphicSchema.type_schemas == {
	# 		'Foo': FooSchema
	# 	}
	# assert PolymorphicSchema.type_schemas == {}

	@restore_schema
	def test_serializable(self):
		"""Ensure Serializable registration works correctly"""
		PolymorphicSchema.type_schemas = {}

		class BarSchema(Schema):
			baz = fields.Email()
			aaa = fields.Float()

			@post_load
			def make(self, data, **kwargs):
				return Bar(**data)

		class BazSchema(Schema):
			foo = fields.Nested(FooSchema)
			bar = fields.Nested(BarSchema)

			@post_load
			def make(self, data, **kwargs):
				return Baz(**data)

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

		assert PolymorphicSchema.type_schemas == {
			'Bar': BarSchema,
			'Baz': BazSchema
		}