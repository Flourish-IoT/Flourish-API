from abc import ABC, abstractmethod
from enum import IntEnum
import logging
from typing import Any, Callable, Tuple, cast

from app.core.models.plant import Plant
from .score_function import ScoreFunction
from app.core.util import Comparable
from sqlalchemy import Column

class ValueRating(IntEnum):
	NoRating = -1
	TooLow = 1,
	Low = 2,
	Nominal = 3
	High = 4,
	TooHigh = 5,

class MinMaxSource(ABC):
	@abstractmethod
	def get_min_max(self):
		raise NotImplementedError

class PlantTypeMinMaxSource(MinMaxSource):
	def __init__(self, plant: Plant, min_col: Column | Any, max_col: Column | Any) -> None:
		self.plant = plant
		self.min_column = cast(Column, min_col)
		self.max_column = cast(Column, max_col)

	def get_min_max(self) -> Tuple[Comparable | None, Comparable | None]:
		plant_type = self.plant.plant_type
		if plant_type is None:
			logging.info('Plant has no plant type associated with it, cannot get min/max')
			return (None, None)

		# dynamically get value corresponding to column
		min = plant_type.get_column_value(self.min_column)
		max = plant_type.get_column_value(self.max_column)

		return (min, max)

class OverrideMinMaxSource(MinMaxSource):
	def get_min_max(self):
		raise NotImplementedError

def target_value_score(min_max_source: MinMaxSource) -> Callable[[Any], Any]:
	def score(value: Comparable) -> ValueRating:
		# TODO: This needs to be expanded
		logging.info(f'Scoring value: {value}')
		min, max = min_max_source.get_min_max()

		if min is None or max is None:
			logging.info('Min or max is none, cannot score value')
			return ValueRating.NoRating

		logging.info(f'min={min}, max={max}')
		match value:
			case n if n < min:
				return ValueRating.TooLow
			case n if n > min and n < max:
				return ValueRating.Nominal
			case n if n > max:
				return ValueRating.TooHigh
			case _:
				return ValueRating.NoRating

	return score

class TargetValueScoreFunction(ScoreFunction):
	min_max_source: MinMaxSource
	def __init__(self, min_max_source: MinMaxSource):
		self.min_max_source = min_max_source

	def score(self, value: Comparable) -> ValueRating:
		# TODO: This needs to be expanded
		logging.info(f'Scoring value: {value}')
		min, max = self.min_max_source.get_min_max()

		if min is None or max is None:
			logging.info('Min or max is none, cannot score value')
			return ValueRating.NoRating

		logging.info(f'min={min}, max={max}')
		match value:
			case n if n < min:
				return ValueRating.TooLow
			case n if n > min and n < max:
				return ValueRating.Nominal
			case n if n > max:
				return ValueRating.TooHigh
			case _:
				return ValueRating.NoRating
