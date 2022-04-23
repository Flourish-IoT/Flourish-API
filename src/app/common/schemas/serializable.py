from functools import wraps
from types import FunctionType
from typing import Any, Callable, Dict, Type
from marshmallow.fields import Field, Nested
from marshmallow import Schema

from app.common.schemas import DynamicSchema, DynamicField, TypeField

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
	"""Registers a class containing a nested Schema with DynamicField and PolymorphicSchema"""
	__schema__: Type[Schema]

	def __init_subclass__(cls, **kwargs) -> None:
		super().__init_subclass__(**kwargs)

		# register all subclasses with the DynamicField
		if cls.__schema__ is None:
			raise ValueError(f"Can't instantiate class {cls} without __schema__ attribute defined")
		DynamicField.register(cls, Nested, {'nested': cls.__schema__})
		DynamicSchema.register(cls, cls.__schema__)

class SerializableType:
	"""Registers a Type with TypeField"""
	def __init_subclass__(cls, **kwargs) -> None:
		super().__init_subclass__(**kwargs)
		# register all subclasses with the TypeField
		TypeField.register(cls)

def serializable_function(func: Callable):
	"""Decorator to register function with TypeField"""
	TypeField.register(func)
	@wraps(func)
	def f(*args, **kwargs):
		return func(*args, **kwargs)
	return f
