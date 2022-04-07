from typing import List, Optional, Type
from marshmallow import Schema, ValidationError
from marshmallow_oneofschema import OneOfSchema

class Serializable:
	"""Registers a class with the PolymorphicSchema"""
	__schema__: Type[Schema] | None

	def __init_subclass__(cls, **kwargs) -> None:
		super().__init_subclass__(**kwargs)
		# register all subclasses with the polymorphic schema loader
		if cls.__schema__ is None:
			raise ValueError("Schema must be defined")
		PolymorphicSchema.register(cls, cls.__schema__)

class PolymorphicSchema(OneOfSchema):
	"""
	Special kind of schema that allows for polymorphic schemas based on Schema type.
	"""
	whitelist: List[Type] | None
	def __init__(self, whitelist: Optional[List[Type[Schema]]] = None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.whitelist = whitelist

	def _is_whitelisted_schema(self, _type: str) -> bool:
		"""Checks whether or not a schema for a type is whitelisted

		Args:
				_type (str): Type of object

		Returns:
				bool: Indicates whether or not type has a schema that is whitelisted
		"""
		if self.whitelist is None:
			return True

		if _type in self.type_schemas:
			obj_schema = self.type_schemas[_type]
			return any([issubclass(obj_schema, whitelisted_schema) for whitelisted_schema in self.whitelist])

		return False

	def get_obj_type(self, obj):
		obj_type: str = super().get_obj_type(obj)

		if not self._is_whitelisted_schema(obj_type):
			raise ValidationError(f'Schema for type {obj_type} is not whitelisted')

		return obj_type

	def get_data_type(self, data):
		data_type: str = super().get_data_type(data)

		if not self._is_whitelisted_schema(data_type):
			raise ValidationError(f'Schema for type {data_type} is not whitelisted')

		return data_type

	@classmethod
	def register(cls, t: Type, schema: Type[Schema]):
		"""All classes that can be dynamically loaded by the polymorphic schema loader must be registered first

		Args:
				type (Type): Class type
				schema (Type[Schema]): Schema to use when serializing/deserializing class
		"""
		# if t.__name__ in cls.type_schemas:
		# 	raise ValueError(f'Class has already been registered: {{{t.__name__}: {cls.type_schemas[t.__name__]}}}')
		cls.type_schemas[t.__name__] = schema