from abc import ABC, abstractmethod
import logging
from typing import Any, Callable, Type, cast
from app.core.models import Device, SensorData
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import Column, Integer

whitelisted_tables = [SensorData, Device]
WhitelistedTable = Type[SensorData] | Type[Device]

class Query(ABC):
	table: WhitelistedTable
	id_column: Column[Integer]
	post_process_function: Callable[[Any], Any] | None

	def __init__(self, table: WhitelistedTable, id_column: Column[Integer] | int , post_process_function: Callable[[Any], Any] | None = None):
		"""Retrieves a value from a table

		Args:
				table (WhitelistedTable): Table to get data from
				id_column (Column[Integer] | int): The ID column of the table
				post_process_function (Callable[[Any], Any] | None, optional): An optional function to further process the data. Defaults to None.

		Raises:
				ValueError: Table is not a whitelisted table
		"""
		if table not in whitelisted_tables:
			raise ValueError(f'Table {table} is restricted')

		self.table = table
		self.id_column = cast(Column[Integer], id_column)
		self.post_process_function = post_process_function

	def post_process(self, value: Any) -> Any:
		"""If post_process function is defined, call it

		Args:
				value (Any): Value to process

		Returns:
				Any: Processed value
		"""
		logging.info('Running post_process')
		if self.post_process_function is not None:
			logging.info('post_process_function is defined, processing')
			return self.post_process_function(value)

		logging.info('post_process_function is None, not processing')
		return value

	@abstractmethod
	def execute(self, id: int, column: Column | Any, session: ScopedSession) -> Any:
		"""Executes query

		Args:
				id (int): ID of value to retrieve
				column (Column | Any): Column value to retrieve
				session (ScopedSession): SQLAlchemy database session

		Returns:
				Any: Query value
		"""
		raise NotImplementedError