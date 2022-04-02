import logging
from typing import Any, Callable
from .query import Query, WhitelistedTable
# from .query import Query, WhitelistedTable
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, Column, TIMESTAMP, exc, Integer
from datetime import datetime, timedelta

class SlopeQuery(Query):
	"""Retrieve the slope of a column from the database"""
	time_start: timedelta
	time_end: timedelta | None
	def __init__(self, table: WhitelistedTable, id_column: Column[Integer] | int, time_start: timedelta, time_end: timedelta | None = None, post_process_function: Callable[[Any], Any] | None = None):
		"""
		Args:
				table (WhitelistedTable): Table to get data from
				id_column (Column[Integer] | int): The ID column of the table
				time_start (timedelta): The starting point to calculate slope
				time_end (timedelta | None, optional): The end point to calculate slope. Defaults to now
				post_process_function (Callable[[Any], Any] | None, optional): An optional function to further process the data. Defaults to None.
		"""
		super().__init__(table, id_column, post_process_function)
		self.time_start = time_start
		self.time_end = time_end

	def execute(self, id: int, column: Column | Any, session: ScopedSession) -> Any:
		logging.info(f'Slope Query. table={self.table}, column={column}, id_column={self.id_column}, id={id}')
		# TODO: manual timescaledb query to get slope over time range
		query = select(column).where(self.id_column == id)

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
