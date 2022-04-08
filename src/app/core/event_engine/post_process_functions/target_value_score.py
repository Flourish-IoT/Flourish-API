from abc import ABC, abstractmethod
from enum import IntEnum
import logging
from typing import Any, Callable, Tuple, cast

import app.core.models as models
from app.common.schemas import Serializable
# from app.core.models.plant import Plant
from app.core.util import Comparable
from sqlalchemy import Column
from functools import partial

from marshmallow_enum import EnumField

class ValueRating(Serializable, IntEnum):
	__field__ = EnumField

	@classmethod
	def __field_kwargs__(cls):
		return {'enum': __class__}

	NoRating = -1
	TooLow = 1,
	Low = 2,
	Nominal = 3
	High = 4,
	TooHigh = 5,

def score(value: Comparable, min: Comparable | None, max: Comparable | None) -> ValueRating:
	# TODO: This needs to be expanded
	logging.info(f'Scoring value: {value}')

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

def _get_plant_min_max(plant: models.Plant, min_col: Column | Any, max_col: Column | Any) -> Tuple[Comparable | None, Comparable | None]:
	plant_type = plant.plant_type
	if plant_type is None:
		logging.info('Plant has no plant type associated with it, cannot get min/max')
		return (None, None)

	# dynamically get value corresponding to column
	min = plant_type.get_column_value(min_col)
	max = plant_type.get_column_value(max_col)
	return (min, max)

def plant_value_score(plant: models.Plant, min_col: Column | Any, max_col: Column | Any) -> Callable[[Any], Any]:
	def _score(value: Comparable) -> ValueRating:
		min, max = _get_plant_min_max(plant, min_col, max_col)
		return score(value, min, max)

	return _score