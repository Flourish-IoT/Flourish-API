from marshmallow.fields import Field
from marshmallow import ValidationError
from pydoc import locate
from inspect import isclass

class GenericField(Field):
	# TODO: whitelist for allowed types?
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

	def _serialize(self, value, attr, obj, **kwargs):
		# get full qualified object name
		module = type(value).__module__

		# TODO: module names for internal types can get pretty long, can we shorten them?
		if module is None or module == 'builtins':
			val_type = type(value).__qualname__
		else:
			val_type = f'{module}.{type(value).__qualname__}'

		# TODO: special field for classes that have a __schema__ property?
		return {
			'value': value,
			'type': val_type
		}

	def _deserialize(self, value, attr, data, **kwargs):
		if 'value' not in value:
			raise ValidationError(f'Generic field requires a value')

		val_type = value.get('type')
		if val_type is None:
			raise ValidationError(f'Generic field requires a type')

		# special case for None
		if val_type == 'NoneType':
			return None

	# TODO: is this a security vulnerability? Not sure if it loads arbitrary modules
		cls = locate(val_type)
		if not isclass(cls):
			raise ValidationError(f'Invalid type')

		return cls(value['value'])