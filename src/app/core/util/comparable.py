from typing import Any, Protocol, TypeVar
from abc import abstractmethod

C = TypeVar("C", bound="Comparable")

class Comparable(Protocol):
	"""From https://github.com/python/typing/issues/59#issuecomment-353878355"""
	@abstractmethod
	def __eq__(self, __x: object) -> bool:
		pass

	@abstractmethod
	def __lt__(self: C, __x: C) -> bool:
		pass

	def __gt__(self: C, __x: C) -> bool:
			return (not self < __x) and self != __x

	def __le__(self: C, __x: C) -> bool:
			return self < __x or self == __x

	def __ge__(self: C, __x: C) -> bool:
			return (not self < __x)