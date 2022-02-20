import logging
from .query import Query
from app.core.models import BaseModel, SensorData
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, Column, TIMESTAMP, exc, Integer

class ValueQuery(Query):
	def __init__(self, table: BaseModel, id_column: Column[Integer], time_column: Column[TIMESTAMP], column: Column):
		super().__init__(table, id_column, time_column, column)

	def execute(self, id: int, session: ScopedSession):
		logging.info(f'Value Query. table={self.table}, column={self.column}, time_column={self.time_column}, id_column={self.id_column}, id={id}')
		query = select(self.column, self.time_column).where(self.id_column == id).order_by(self.time_column.desc()).limit(1)

		try:
			value = session.execute(query).scalar_one()
		except exc.DatabaseError as e:
			logging.error('Failed to execute query')
			logging.exception(e)
			raise e

		logging.info(f'Latest value: {value}')
		return value