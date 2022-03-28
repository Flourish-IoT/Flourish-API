
from abc import ABC
from typing import Type
from marshmallow import Schema
from marshmallow_oneofschema import OneOfSchema

class Serializable(ABC):
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
	@classmethod
	def register(cls, t: Type, schema: Type[Schema]):
		"""All classes that can be dynamically loaded by the polymorphic schema loader must be registered first

		Args:
				type (Type): Class type
				schema (Type[Schema]): Schema to use when serializing/deserializing class
		"""
		if t.__name__ in cls.type_schemas:
			raise ValueError(f'Class has already been registered: {{{t.__name__}: {cls.type_schemas[t.__name__]}}}')
		cls.type_schemas[t.__name__] = schema