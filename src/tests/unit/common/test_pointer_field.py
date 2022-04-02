from dataclasses import dataclass
from datetime import timedelta
from marshmallow import fields, post_load, Schema
from app.common.utils import PointerField
import pytest


class FooSchema(Schema):
	foo = PointerField()

@dataclass
class Foo():
	foo: bool

class TestPointerField:
	def test_dump(self):
		"""Ensure polymorphic schema is registering correctly"""
		f = Foo(foo=True)
		schema = FooSchema()
		schema.context = {'bar': True, 'baz': False}
		res = schema.dump(f)

	def test_load(self):
		pass