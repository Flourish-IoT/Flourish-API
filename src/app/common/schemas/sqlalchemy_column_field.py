from marshmallow.fields import Field
from marshmallow import ValidationError
from sqlalchemy.orm import InstrumentedAttribute
from pydoc import locate
from inspect import isclass

class SQLAlchemyColumnField(Field):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

	def _serialize(self, value, attr, obj, **kwargs):
		if not isinstance(value, InstrumentedAttribute) and value is not None:
			raise ValidationError('Value must be a column')

		if value is None:
			return {
				'column': None,
				'table': None
			}

		table = value.class_

		# store column key and get table type
		return {
			'column': value.key,
			# TODO: could be cleaner by registering tables and using a short name as a lookup
			'table': f'{table.__module__}.{table.__qualname__}'
		}

	def _deserialize(self, value, attr, data, **kwargs):
		if not isinstance(value, dict):
			raise ValidationError('Invalid column format')

		if 'column' not in value:
			raise ValidationError('Value missing column')

		if 'table' not in value:
			raise ValidationError('Value missing table')

		col = value['column']
		table = value['table']

		if col is None and table is None:
			return None

	# TODO: is this a security vulnerability? Not sure if it loads arbitrary modules
		cls = locate(table)
		if not isclass(cls):
			raise ValidationError(f'Invalid type')

		column = getattr(cls, col, None)
		if column is None:
			raise ValidationError('Invalid column')

		return column