import logging
from typing import Any, Callable, cast

from app.common.schemas import SQLAlchemyColumnField
from . import Query, WhitelistedTable, QuerySchema
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, Column, TIMESTAMP, exc, Integer
from datetime import datetime

from marshmallow import fields

#######################
# Schemas
#######################
class ValueQuerySchema(QuerySchema):
	order_column = SQLAlchemyColumnField()
#######################

class ValueQuery(Query):
	"""Retrieve a single value from the database"""
	__schema__ = ValueQuerySchema

	order_column: Column | None
	def __init__(self, table: WhitelistedTable, id_column: Column[Integer] | int , order_column: Column | Any = None, post_process_function: Callable[[Any], Any] | None = None):
		"""Retrieves a single value from the database

		Args:
				table (WhitelistedTable): Table to get data from
				id_column (Column[Integer] | int): The ID column of the table
				order_column (Column | Any, optional): _description_. Defaults to None.
				post_process_function (Callable[[Any], Any] | None, optional): An optional function to further process the data. Defaults to None.

		Raises:
				ValueError: Table is not a whitelisted table
		"""
		super().__init__(table, id_column, post_process_function)
		self.order_column = cast(Column | None, order_column)

	"""Retrieves a single value from the database"""
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

		logging.info(f'Latest value: {value}')

		return self.post_process(value)