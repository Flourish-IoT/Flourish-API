from copy import deepcopy
from enum import Enum
from typing import Any, Type, TypeVar
from sqlalchemy.orm.attributes import InstrumentedAttribute

T = TypeVar('T', bound=Enum)

class EnumValuesMixin:
	"""Enum mixin to inject the `values` function that returns all valid enum values. Must be declared before Enum type

	Usage::

		class Foo(EnumValuesMixin, Enum):
			BAR = 1,
			BAZ = 2,

		print(Foo.values())
		['BAR', 'BAZ']
	"""
	@classmethod
	def values(cls: Type[T]): # type: ignore
		"""
		Returns all valid enum values
		"""
		return [e.name for e in cls]