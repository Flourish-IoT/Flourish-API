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
	order_column: Column | None
	post_process_function: Callable[[Any], Any] | None

	def __init__(self, table: WhitelistedTable, id_column: Column[Integer] | int , order_column: Column | Any = None, post_process_function: Callable[[Any], Any] | None = None):
		if table not in whitelisted_tables:
			raise ValueError(f'Table {table} is restricted')

		self.table = table
		self.id_column = cast(Column[Integer], id_column)
		self.order_column = cast(Column | None, order_column)
		self.post_process_function = post_process_function

	def post_process(self, value: Any):
		"""If post_process function is defined, call it

		Args:
				value (Any): _description_

		Returns:
				_type_: _description_
		"""
		logging.info('Running post_process')
		if self.post_process_function is not None:
			logging.info('post_process_function is defined, processing')
			return self.post_process_function(value)

		logging.info('post_process_function is None, not processing')
		return value

	@abstractmethod
	def execute(self, id: int, column: Column | Any, session: ScopedSession) -> Any:
		raise NotImplementedError