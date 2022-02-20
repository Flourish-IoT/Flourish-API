from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class DefaultScoreFunction(ABC, Generic[T]):
	"""Does not process the incoming value"""
	def score(self, value: T) -> T:
		return value
