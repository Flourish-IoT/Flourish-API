import logging
from typing import Any
from .query import Query, WhitelistedTable
from app.core.models import BaseModel, SensorData
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, Column, TIMESTAMP, exc, Integer
from datetime import datetime

class ValueQuery(Query):
	def __init__(self, table: WhitelistedTable, id_column: Column[Integer] | int, time_column: Column[TIMESTAMP] | datetime):
		super().__init__(table, id_column, time_column)

	def execute(self, id: int, column: Column | Any, session: ScopedSession):
		logging.info(f'Value Query. table={self.table}, column={column}, time_column={self.time_column}, id_column={self.id_column}, id={id}')
		query = select(column).where(self.id_column == id).order_by(self.time_column.desc()).limit(1)

		try:
			value = session.execute(query).scalar_one()
		except exc.DatabaseError as e:
			logging.error('Failed to execute query')
			logging.exception(e)
			raise e

		logging.info(f'Latest value: {value}')
		return value