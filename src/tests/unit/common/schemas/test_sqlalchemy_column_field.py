from dataclasses import dataclass
from typing import Any
from marshmallow import fields, post_load, Schema, ValidationError
from sqlalchemy import Column, Integer, VARCHAR
import pytest

from app.common.schemas import SQLAlchemyColumnField
from app.core.models import BaseModel

class BarSchema(Schema):
	col = SQLAlchemyColumnField()

	@post_load
	def make(self, data, **kwargs):
		return Bar(**data)

class Foo(BaseModel):
	__tablename__ = 'test'
	a = Column(Integer, primary_key=True)
	b = Column(VARCHAR)

@dataclass
class Bar():
	col: Column | None

class TestSQLAlchemyColumnField:
	@pytest.mark.parametrize('value, expected', [
		(Bar(Foo.a), {
			'col': {
				'column': 'a',
				'table': 'test_sqlalchemy_column_field.Foo'
			}
		}),
		(Bar(Foo.b), {
			'col': {
				'column': 'b',
				'table': 'test_sqlalchemy_column_field.Foo'
			}
		}),
		(Bar(None), {
			'col': {
				'column': None,
				'table': None,
			}
		})
	])
	def test_dump(self, value, expected):
		res = BarSchema().dump(value)
		assert res == expected

	@pytest.mark.parametrize('value, expected', [
		({
			'col': {
				'column': 'a',
				'table': 'test_sqlalchemy_column_field.Foo'
			}
		}, Bar(Foo.a)),
		({
			'col': {
				'column': 'b',
				'table': 'test_sqlalchemy_column_field.Foo'
			}
		}, Bar(Foo.b)),
		({
			'col': {
				'column': None,
				'table': None
			}
		}, Bar(None))
	])
	def test_load(self, value, expected):
		res = BarSchema().load(value)
		assert res == expected

	@pytest.mark.parametrize('value', [
		({
			'col': {
				'column': 'DoesNotExist',
				'table': 'test_sqlalchemy_column_field.Foo'
			}
		}),
		({
			'col': {
				'column': 'Foo',
				'table': 'DoesNotExist'
			}
		}),
		({
			'col': 'BadValue'
		}),
		({
			'col':{
				'column': 'MissingTableField'
			}
		}),
		({
			'col':{
				'table': 'MissingColumnField'
			}
		}),
	])
	def test_load_raises(self, value):
		with pytest.raises(ValidationError):
			BarSchema().load(value)
