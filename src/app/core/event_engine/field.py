import logging
from typing import Any, Dict

from app.core.event_engine.queries import Query
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import Column

class Field:
	field: Column
	queries: Dict[str, Query]

	def __init__(self, field: Column | Any, queries: Dict[str, Query]) -> None:
		self.field = field
		self.queries = queries

	def get_value(self, id: int, session: ScopedSession):
		logging.info(f'Getting value for field {self.field} and id {id}')
		value = {}
		for field, query in self.queries.items():
			value[field] = query.execute(id, self.field, session)

		logging.info(f'Value={value}')
		return value