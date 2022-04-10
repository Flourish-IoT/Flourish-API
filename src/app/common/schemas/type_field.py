from types import NoneType
from typing import Any, Callable, Dict, List, Optional, Type
from marshmallow.fields import Field
from marshmallow import ValidationError, Schema
from inspect import isclass, isfunction


class TypeField(Field):
	# mapping of qualname to python type. Used to lookup type when deserializing
	type_name_mapping: Dict[str, type] = {**{mapping.__qualname__: mapping for mapping in Schema.TYPE_MAPPING.keys()}, NoneType.__qualname__: NoneType}

	whitelist: List[Type] | None = None

	def __init__(self, whitelist: Optional[List[Type]] = None, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.whitelist = whitelist

	# TODO: strict parameter to disable checking inherited classes in whitelist?
	def is_whitelisted_type(self, _type: Type) -> bool:
		"""Checks whether or not a field for a type is whitelisted

		Args:
				_type (Type): Type of object

		Returns:
				bool: Indicates whether or not type has a field that is whitelisted
		"""
		if self.whitelist is None:
			return True

		return any([issubclass(_type, whitelisted_class) for whitelisted_class in self.whitelist])

	def _serialize(self, value: Type | Callable | Any, attr, obj, **kwargs):
		if value is None:
			return None

		if not isclass(value) and not isfunction(value):
			raise ValidationError(f'Field value must be a Type or Function')

		if not self.is_whitelisted_type(value):
			raise ValidationError(f'Type or Function {value} is not allowed')

		# use the type name to check if type has been registed
		if value.__qualname__ not in self.type_name_mapping:
			raise ValidationError(f'No Field registered for Type or Function {value}')

		return value.__qualname__

	def _deserialize(self, value, attr, data, **kwargs):
		if value is None:
			return None

		_type = self.type_name_mapping.get(value)
		if _type is None:
			raise ValidationError(f'No Field registered for type {value}')

		if not self.is_whitelisted_type(_type):
			raise ValidationError(f'Type {_type} is not allowed')

		return _type

	@classmethod
	def register(cls, _type: Type):
		"""All classes that can be loaded by the TypeField must be registered first

		Args:
				type (Type): Class type
		"""
		cls.type_name_mapping[_type.__qualname__] = _type
