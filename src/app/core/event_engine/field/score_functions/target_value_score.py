from enum import IntEnum
from .score_function import ScoreFunction
from typing import Generic, TypeVar

from app.core.util import Comparable

T = TypeVar('T', bound=Comparable)

class ValueRating(IntEnum):
	NoRating = -1
	TooLow = 1,
	Low = 2,
	Nominal = 3
	High = 4,
	TooHigh = 5,

class TargetValueScoreFunction(ScoreFunction, Generic[T]):
	def __init__(self, min: T, max: T):
		if min > max:
			raise ValueError('min must be less than max')

		self.min = min
		self.max = max

	def score(self, value: T) -> ValueRating:
		# TODO: This needs to be expanded
		match value:
			case n if n < self.min:
				return ValueRating.TooLow
			case n if n > self.min and n < self.max:
				return ValueRating.Nominal
			case n if n > self.max:
				return ValueRating.TooHigh
			case _:
				return ValueRating.NoRating
