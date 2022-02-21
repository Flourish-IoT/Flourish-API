import logging
from typing import Any
from .query import Query, WhitelistedTable
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, Column, TIMESTAMP, exc, Integer
from datetime import datetime

class ValueQuery(Query):
	def __init__(self, table: WhitelistedTable, id_column: Column[Integer] | int, order_column: Column | Any = None):
		super().__init__(table, id_column, order_column)

	def execute(self, id: int, column: Column | Any, session: ScopedSession):
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
			raise e

		logging.info(f'Latest value: {value}')
		return value