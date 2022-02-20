import typing
from typing import Any, Protocol
from abc import abstractmethod

C = typing.TypeVar("C", bound="Comparable")

class Comparable(Protocol):
	"""From https://github.com/python/typing/issues/59#issuecomment-353878355"""
	@abstractmethod
	def __eq__(self, other: Any) -> bool:
		pass

	@abstractmethod
	def __lt__(self: C, other: C) -> bool:
		pass

	def __gt__(self: C, other: C) -> bool:
		return (not self < other) and self != other

	def __le__(self: C, other: C) -> bool:
		return self < other or self == other

	def __ge__(self: C, other: C) -> bool:
		return (not self < other)