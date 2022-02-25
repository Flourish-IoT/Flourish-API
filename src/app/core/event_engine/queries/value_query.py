import logging
from typing import Any
from .query import Query
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, Column, TIMESTAMP, exc, Integer
from datetime import datetime

class ValueQuery(Query):
	def execute(self, id: int, column: Column | Any, session: ScopedSession) -> Any:
		logging.info(f'Value Query. table={self.table}, column={column}, order_column={self.order_column}, id_column={self.id_column}, id={id}')
		query = select(column).where(self.id_column == id)

		if self.order_column is not None:
			query = query.order_by(self.order_column.desc())

		query = query.limit(1)

		try:
			value = session.execute(query).scalar_one()
		except exc.DatabaseError as e:
			logging.error('Failed to execute query')
			logging.exception(e)
			return None
			raise e

		logging.info(f'Latest value: {value}')

		return self.post_process(value)