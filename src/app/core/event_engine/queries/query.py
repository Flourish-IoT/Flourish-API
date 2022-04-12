from abc import ABC, abstractmethod
import logging
from typing import Any, Callable, Optional, Type, cast
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import Column, Integer
from app.common.schemas import SQLAlchemyColumnField, SerializableClass, TypeField, DynamicField
from app.core.event_engine.events import Event
from app.core.event_engine.post_process_functions import PostProcessor
import app.core.models as models

from marshmallow import Schema, fields

#######################
# Schemas
#######################
class QuerySchema(Schema):
	table = TypeField([models.SensorData, models.Device])
	id_column = SQLAlchemyColumnField()
	post_processor = DynamicField([PostProcessor], allow_none = True)
#######################

whitelisted_tables = [models.SensorData, models.Device]
WhitelistedTable = Type[models.SensorData] | Type[models.Device]

class Query(SerializableClass, ABC):
	__schema__ = QuerySchema

	table: WhitelistedTable
	id_column: Column[Integer]
	post_processor: PostProcessor | None

	def __init__(self, table: WhitelistedTable, id_column: Column[Integer] | int , post_processor: Optional[PostProcessor] = None):
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
		self.post_processor = post_processor

	def post_process(self, event: Event, value: Any) -> Any:
		"""If post_process function is defined, call it

		Args:
				value (Any): Value to process

		Returns:
				Any: Processed value
		"""
		logging.info('Running post_process')
		if self.post_processor is not None:
			logging.info('post_process_function is defined, processing')
			return self.post_processor.process(value, event)

		logging.info('post_process_function is None, not processing')
		return value

	@abstractmethod
	def execute(self, id: int, column: Column | Any, session: ScopedSession, event: Event) -> Any:
		"""Executes query

		Args:
				id (int): ID of value to retrieve
				column (Column | Any): Column value to retrieve
				session (ScopedSession): SQLAlchemy database session

		Returns:
				Any: Query value
		"""
		raise NotImplementedError