from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Type, TypeVar, cast
from app.core.models import Device, SensorData
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import Column, TIMESTAMP, Integer

whitelisted_tables = [SensorData, Device]
WhitelistedTable = SensorData | Device

class Query(ABC):
	table: WhitelistedTable
	id_column: Column[Integer]
	order_column: Column | None

	def __init__(self, table: WhitelistedTable, id_column: int | Column[Integer], order_column: Any | Column = None):
		if table not in whitelisted_tables:
			raise ValueError(f'Table {table} is restricted')

		self.table = table
		self.id_column = cast(Column[Integer], id_column)
		self.order_column = cast(Column | None, order_column)

	@abstractmethod
	def execute(self, id: int, column: Column | Any, session: ScopedSession) -> Any:
		raise NotImplementedError