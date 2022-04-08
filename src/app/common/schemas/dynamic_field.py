from enum import Enum
from types import NoneType
from typing import Any, Dict, List, Optional, Tuple, Type
from marshmallow.fields import Field, Raw, Nested
from marshmallow import ValidationError, Schema
from pydoc import locate
from inspect import isclass

from app.common.utils.polymorphic_schema import PolymorphicSchema

class Serializable:
	"""Registers a class containing a Field with DynamicField"""
	__field__: Type[Field]

	@classmethod
	def __field_kwargs__(cls) -> Dict[str, Any]:
		"""Returns the field specific kwargs"""
		return {}

	def __init_subclass__(cls, **kwargs) -> None:
		super().__init_subclass__(**kwargs)

		# register all subclasses with the DynamicField
		if cls.__field__ is None:
			raise ValueError(f"Can't instantiate class {cls} without __field__ attribute defined")
		DynamicField.register(cls, cls.__field__, cls.__field_kwargs__())

class SerializableClass:
	"""Registers a class containing a nested Schema with DynamicField"""
	__schema__: Type[Schema]

	def __init_subclass__(cls, **kwargs) -> None:
		super().__init_subclass__(**kwargs)

		# register all subclasses with the DynamicField
		if cls.__schema__ is None:
			raise ValueError(f"Can't instantiate class {cls} without __schema__ attribute defined")
		DynamicField.register(cls, Nested, {'nested': cls.__schema__})
		PolymorphicSchema.register(cls, cls.__schema__)

class DynamicField(Field):
	"""Dynamically loads/dumps a field"""

	# should list be dynamic?
	# mapping of qualname to ( Field, field kwargs )
	type_mapping: Dict[Type, Tuple[Type[Field], Dict[str, Any]]] = {**{mapping: (field, {}) for mapping, field in Schema.TYPE_MAPPING.items()}, NoneType: ( Raw, {} )}

	# mapping of qualname to python type. Used to lookup type when deserializing
	type_name_mapping: Dict[str, Type] = {mapping.__qualname__: mapping for mapping in type_mapping.keys()}

	field_args = []
	field_kwargs = {}
	whitelist: List[Type] | None = None

	def __init__(self, whitelist: Optional[List[Type]] = None, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.field_args = args
		self.field_kwargs = kwargs
		self.whitelist = whitelist

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

	def _serialize(self, value, attr, obj, **kwargs):
		if not self.is_whitelisted_type(type(value)):
			raise ValidationError(f'Type {type(value)} is not allowed')

		# use the value type to find the field used to serialize it
		if type(value) not in self.type_mapping:
			raise ValidationError(f'No Field registered for type {type(value)}')

		field, field_kwargs = self.type_mapping[type(value)]

		return {
			'value': field(*self.field_args, **field_kwargs, **self.field_kwargs)._serialize(value, attr, obj, **kwargs),
			# 'value': field(*self.field_args, **field_kwargs, **self.field_kwargs).serialize(attr, obj, **kwargs),
			'type': type(value).__qualname__
		}

	def _deserialize(self, value, attr, data, **kwargs):
		if 'value' not in value:
			raise ValidationError(f'Dynamic field requires a value')

		# get the type associated with the field
		val_type = value.get('type')
		if val_type is None:
			raise ValidationError(f'Dynamic field requires a type')

		_type = self.type_name_mapping.get(val_type)
		if _type is None:
			raise ValidationError(f'No Field registered for type {val_type}')

		if not self.is_whitelisted_type(_type):
			raise ValidationError(f'Type {_type} is not allowed')

		# use type to lookup field
		field, field_kwargs = self.type_mapping[_type]

		# use field to deserialize value
		return field(*self.field_args, **field_kwargs, **self.field_kwargs).deserialize(value['value'], 'value', value, **kwargs)

	@classmethod
	def register(cls, _type: Type, field: Type[Field], field_kwargs: Dict[str, Any] = {}):
		"""All classes that can be loaded by the dynamic field must be registered first

		Args:
				type (Type): Class type
				schema (Type[Field]): Field to use when serializing/deserializing class
		"""
		cls.type_mapping[_type] = (field, field_kwargs)
		cls.type_name_mapping[_type.__qualname__] = _type