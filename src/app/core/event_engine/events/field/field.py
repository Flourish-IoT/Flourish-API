from typing import Any
from .queries import Query
from .score_functions import ScoreFunction
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import Column


class Field:
	field: Column
	query: Query
	score_function: ScoreFunction | None

	def __init__(self, field: Column | Any, query: Query, score_function: ScoreFunction = None) -> None:
		self.field = field
		self.query = query
		self.score_function = score_function

	def get_value(self, id: int, session: ScopedSession):
		value = self.query.execute(id, self.field, session)

		# if score_function is defined, use it to process value
		if self.score_function:
			value = self.score_function.score(value)

		return value