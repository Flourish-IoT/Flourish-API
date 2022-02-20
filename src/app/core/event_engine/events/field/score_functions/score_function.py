from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar('T')

class ScoreFunction(ABC, Generic[T]):
	@abstractmethod
	def score(self, value: T) -> Any:
		raise NotImplementedError