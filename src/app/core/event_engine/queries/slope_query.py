import logging
from typing import Any, Callable, Optional

from app.core.event_engine.post_process_functions import PostProcessor
from . import Query, WhitelistedTable, QuerySchema
from app.core.event_engine.events import Event
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, Column, TIMESTAMP, exc, Integer
from datetime import datetime, timedelta

from marshmallow import fields

#######################
# Schemas
#######################
class SlopeQuerySchema(QuerySchema):
	time_start = fields.TimeDelta()
	time_end = fields.TimeDelta(required=False, default=None)
#######################

class SlopeQuery(Query):
	"""Retrieve the slope of a column from the database"""
	__schema__ = SlopeQuerySchema

	time_start: timedelta
	time_end: timedelta | None
	def __init__(self, table: WhitelistedTable, id_column: Column[Integer] | int, time_start: timedelta, time_end: timedelta | None = None, post_processor: Optional[PostProcessor] = None):
		"""
		Args:
				table (WhitelistedTable): Table to get data from
				id_column (Column[Integer] | int): The ID column of the table
				time_start (timedelta): The starting point to calculate slope
				time_end (timedelta | None, optional): The end point to calculate slope. Defaults to now
				post_process_function (Callable[[Any], Any] | None, optional): An optional function to further process the data. Defaults to None.
		"""
		super().__init__(table, id_column, post_processor)
		self.time_start = time_start
		self.time_end = time_end

	def execute(self, event: Event, id: int, column: Column | Any, session: ScopedSession) -> Any:
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

		return self.post_process(event, value)
