from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Any
from app.common.schemas import TypeField
from app.common.schemas.serializable import serializable_function
from app.core.event_engine.post_process_functions import ValueRating
from marshmallow import fields, post_load, Schema, ValidationError
import pytest
from copy import deepcopy

class FooSchema(Schema):
	foo = TypeField(allow_none=True)

	@post_load
	def make(self, data, **kwargs):
		return Foo(**data)

@dataclass
class Foo():
	foo: Any

class Bar():
	baz: Any

def test_func():
	pass

class TestTypeField:
	@pytest.mark.parametrize('value, expected, cls', [
		(Foo(foo=int), {
			'foo': 'int'
		}, None),
		(Foo(foo=str), {
			'foo': 'str'
		}, None),
		(Foo(foo=datetime), {
			'foo': 'datetime'
		}, None),
		(Foo(foo=None), {
			'foo': None
		}, None),
		(Foo(foo=ValueRating), {
			'foo': 'ValueRating'
		}, ValueRating),
		(Foo(foo=test_func), {
			'foo': 'test_func'
		}, test_func),
	])
	def test_dump(self, value, expected, cls):
		if cls is not None:
			TypeField.register(cls)

		res = FooSchema().dump(value)
		assert res == expected

	@pytest.mark.parametrize('value', [
		(Foo(foo=Bar)),
		(Foo(foo=ValueRating)),
		(Foo(foo=3)),
		(Foo(foo='bar')),
	])
	def test_dump_raises(self, value):
		with pytest.raises(ValidationError):
			FooSchema().dump(value)

	@pytest.mark.parametrize('value, whitelist, cls', [
		(Foo(foo=int), [int], None),
		(Foo(foo=int), [int, float, str], None),
		(Foo(foo=ValueRating), [ValueRating], ValueRating),
		(Foo(foo=ValueRating), [int], ValueRating),
	])
	def test_dump_whitelist(self, value, whitelist, cls):
		if cls is not None:
			TypeField.register(cls)

		class FooSchema(Schema):
			foo = TypeField(whitelist)
		FooSchema().dump(value)

	@pytest.mark.parametrize('value, whitelist, cls', [
		(Foo(foo=int), [str], None),
		(Foo(foo=str), [int, float, datetime], None),
		(Foo(foo=ValueRating), [str], ValueRating),
	])
	def test_dump_whitelist_raises(self, value, whitelist, cls):
		if cls is not None:
			TypeField.register(cls)

		class FooSchema(Schema):
			foo = TypeField(whitelist)

		with pytest.raises(ValidationError):
			FooSchema().dump(value)

	@pytest.mark.parametrize('value, expected', [
		({
			'foo': 'int'
		}, Foo(foo=int)),
		({
			'foo': 'str'
		}, Foo(foo=str)),
		({
			'foo': 'datetime'
		}, Foo(foo=datetime)),
		({
			'foo': None
		}, Foo(foo=None)),
	])
	def test_load(self, value, expected):
		res = FooSchema().load(value)
		assert res == expected

	@pytest.mark.parametrize('value', [
		({
			'foo': 'ValueRating'
		}),
		({
			'foo': 'Bar'
		}),
	])
	def test_load_raises(self, value):
		with pytest.raises(ValidationError):
			FooSchema().load(value)

	@pytest.mark.parametrize('value, whitelist, cls', [
		({
			'foo': 'int'
		}, [int], None),
		({
			'foo': 'int'
		}, [int, str, float], None),
		({
			'foo': 'ValueRating'
		}, [ValueRating], ValueRating),
		({
			'foo': 'ValueRating'
		}, [int], ValueRating),
	])
	def test_load_whitelist(self, value, whitelist, cls):
		if cls is not None:
			TypeField.register(cls)

		class FooSchema(Schema):
			foo = TypeField(whitelist)
		FooSchema().load(value)

	@pytest.mark.parametrize('value, whitelist, cls', [
		({
			'foo': 'int'
		}, [str], None),
		({
			'foo': 'str'
		}, [int, float, datetime], None),
		({
			'foo': 'ValueRating'
		}, [str], ValueRating),
	])
	def test_load_whitelist_raises(self, value, whitelist, cls):
		if cls is not None:
			TypeField.register(cls)

		class FooSchema(Schema):
			foo = TypeField(whitelist)

		with pytest.raises(ValidationError):
			FooSchema().load(value)