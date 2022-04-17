from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
import logging
from typing import Any, Callable, Tuple, cast
from app.common.schemas import Serializable, SQLAlchemyColumnField
from app.core.util import Comparable
from app.core.event_engine.events import Event, PlantEventType
from . import PostProcessor, PostProcessorSchema
from app.core.models import Plant

from sqlalchemy import Column
from functools import partial

from marshmallow_enum import EnumField
from marshmallow import post_load

# TODO: combine this file with whatever serb and akshiv are working on

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

def _get_plant_min_max(plant: Plant, min_col: Column | Any, max_col: Column | Any) -> Tuple[Comparable | None, Comparable | None]:
	plant_type = plant.plant_type
	if plant_type is None:
		logging.info('Plant has no plant type associated with it, cannot get min/max')
		return (None, None)

	# dynamically get value corresponding to column
	min = plant_type.get_column_value(min_col)
	max = plant_type.get_column_value(max_col)
	return (min, max)

class PlantValueScoreSchema(PostProcessorSchema):
	min_col = SQLAlchemyColumnField()
	max_col = SQLAlchemyColumnField()

	@post_load
	def make(self, data, **kwargs):
		return PlantValueScore(**data)

@dataclass
class PlantValueScore(PostProcessor):
	__schema__ = PlantValueScoreSchema

	min_col: Column | Any
	max_col: Column | Any

	def process(self, value: Comparable, event: Event) -> ValueRating:
		if not isinstance(event, PlantEventType):
			raise ValueError('Score function incompatible with event')

		min, max = _get_plant_min_max(event.plant, self.min_col, self.max_col)
		return score(value, min, max)