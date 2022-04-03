from dataclasses import dataclass
from datetime import timedelta
from marshmallow import fields, post_load, Schema
from app.common.utils import MappedField
import pytest


class FooSchema(Schema):
	foo = MappedField('field_context', mapping_func=lambda x: x.baz)

	@post_load
	def make(self, data, **kwargs):
		return Foo(**data)

@dataclass
class Bar():
	baz: int

@dataclass
class Foo():
	foo: Bar

class TestMappedField:
	def test_dump(self):
		"""Ensure field dumps correctly"""
		f = Foo(foo=Bar(baz=4))
		schema = FooSchema()
		res = schema.dump(f)
		assert res == {
			'foo': 4
		}
		print(res)

	def test_load(self):
		obj = {
			'foo': 4
		}
		schema = FooSchema()
		schema.context = {
			'field_context': {
				4: Bar(baz=4)
			}
		}
		res = schema.load(obj)
		assert res == Foo(foo=Bar(baz=4))