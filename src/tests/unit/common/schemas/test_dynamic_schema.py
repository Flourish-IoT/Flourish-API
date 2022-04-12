from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta
from app.common.schemas import DynamicSchema, SerializableClass
from marshmallow import fields, post_load, Schema, ValidationError
import pytest
from functools import wraps

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

class FooBarSchema(FooSchema):
	baz = fields.String()

	@post_load
	def make(self, data, **kwargs):
		return FooBar(**data)
@dataclass
class FooBar(Foo):
	__schema__ = FooBarSchema
	# used for testing inheritance for whitelist
	baz: str

class AaaSchema(Schema):
	a = fields.String()
	b = fields.Float()

	@post_load
	def make(self, data, **kwargs):
		return Aaa(**data)
@dataclass
class Aaa():
	# used for testing manual registration
	__schema__ = AaaSchema
	a: str
	b: float

class TestDynamicSchema:
	def test_register(self):
		"""Ensure polymorphic schema is registering correctly"""
		DynamicSchema.type_schemas = {}
		DynamicSchema.register(Foo, Foo.__schema__)

		assert DynamicSchema.type_schemas == {
			'Foo': FooSchema
		}

		DynamicSchema.register(Aaa, Aaa.__schema__)

		assert DynamicSchema.type_schemas == {
			'Foo': FooSchema,
			'Aaa': AaaSchema
		}

	def test_serializable(self):
		"""Ensure Serializable registration works correctly"""
		DynamicSchema.type_schemas = {}

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
		class Bar(SerializableClass):
			__schema__ = BarSchema
			baz: str
			aaa: float

		@dataclass
		class Baz(SerializableClass):
			__schema__ = BazSchema
			foo: Foo
			bar: Bar

		assert DynamicSchema.type_schemas == {
			'Bar': BarSchema,
			'Baz': BazSchema
		}

	@pytest.mark.parametrize('cls, value, expected', [
		(Foo, Foo(foo=True, bar=2), {
			'type': 'Foo',
			'foo': True,
			'bar': 2
		}),
		(Aaa, Aaa(a='Test', b=2.3), {
			'type': 'Aaa',
			'a': 'Test',
			'b': 2.3
		}),
	])
	def test_dump(self, cls, value, expected):
		"""Ensure polymorphic schema is dumped correctly"""
		DynamicSchema.type_schemas = {}
		DynamicSchema.register(cls, cls.__schema__)

		res = DynamicSchema().dump(value)
		assert res == expected

	@pytest.mark.parametrize('cls, value, expected', [
		(Foo, {
			'type': 'Foo',
			'foo': True,
			'bar': 2
		}, Foo(foo=True, bar=2)),
		(Aaa, {
			'type': 'Aaa',
			'a': 'Test',
			'b': 2.3
		}, Aaa(a='Test', b=2.3)),
	])
	def test_load(self, cls, value, expected):
		"""Ensure polymorphic schema is loaded correctly"""
		DynamicSchema.type_schemas = {}
		DynamicSchema.register(cls, cls.__schema__)

		res = DynamicSchema().load(value)
		assert res == expected

	@pytest.mark.parametrize('cls, value, whitelisted', [
		(Foo, Foo(foo=True, bar=2), [AaaSchema]),
		(Aaa, Aaa(a='foo', b=3.2), [FooSchema, FooBarSchema]),
	])
	def test_whitelist_dump_raises(self, cls, value, whitelisted):
		# test that whitelist raises error if dumping a value not in whitelist
		DynamicSchema.type_schemas = {}
		DynamicSchema.register(cls, cls.__schema__)

		with pytest.raises(ValidationError):
			DynamicSchema(whitelisted).dump(value)

	@pytest.mark.parametrize('cls, value, whitelisted', [
		(Foo, Foo(foo=True, bar=2), [FooSchema]),
		(Aaa, Aaa(a='foo', b=3.2), [AaaSchema]),
		(FooBar, FooBar(foo=True, bar=2, baz='Aaa'), [FooSchema]),
	])
	def test_whitelist_dump(self, cls, value, whitelisted):
		# test that whitelist allows values in whitelist to be dumped
		DynamicSchema.type_schemas = {}
		DynamicSchema.register(cls, cls.__schema__)

		DynamicSchema(whitelisted).dump(value)

	@pytest.mark.parametrize('cls, value, whitelisted', [
		(Foo, {
			'type': 'Foo',
			'foo': True,
			'bar': 2
		}, [FooSchema]),
		(Aaa, {
			'type': 'Aaa',
			'a': 'Test',
			'b': 2.3
		}, [AaaSchema]),
		(FooBar, {
			'type': 'FooBar',
			'foo': True,
			'bar': 2,
			'baz': 's'
		}, [FooSchema]),
	])
	def test_whitelist_load(self, cls, value, whitelisted):
		# test that whitelist allows values that are in the whitelist to be loaded
		DynamicSchema.type_schemas = {}
		DynamicSchema.register(cls, cls.__schema__)

		DynamicSchema(whitelisted).load(value)

	@pytest.mark.parametrize('cls, value, whitelisted', [
		(Foo, {
			'type': 'Foo',
			'foo': True,
			'bar': 2
		}, [AaaSchema]),
		(FooBar, {
			'type': 'FooBar',
			'foo': True,
			'bar': 2,
			'baz': 's'
		}, [AaaSchema]),
	])
	def test_whitelist_load_raises(self, cls, value, whitelisted):
		# test that whitelist allows values that are in the whitelist to be loaded
		DynamicSchema.type_schemas = {}
		DynamicSchema.register(cls, cls.__schema__)

		with pytest.raises(ValidationError):
			DynamicSchema(whitelisted).load(value)