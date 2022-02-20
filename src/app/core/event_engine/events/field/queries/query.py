from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Type, TypeVar, cast
from app.core.models import BaseModel, SensorData
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import Column, TIMESTAMP, Integer

whitelisted_tables = [SensorData]
WhitelistedTable = SensorData

class Query(ABC):
	table: BaseModel
	id_column: Column[Integer]
	time_column: Column[TIMESTAMP]

	def __init__(self, table: WhitelistedTable, id_column: int | Column[Integer], time_column: datetime | Column[TIMESTAMP]):
		if table not in whitelisted_tables:
			raise ValueError(f'Table {table} is restricted')

		self.time_column = cast(Column[TIMESTAMP], time_column)
		self.id_column = cast(Column[Integer], id_column)
		self.table = table

	@abstractmethod
	def execute(self, id: int, column: Column | Any, session: ScopedSession) -> Any:
		raise NotImplementedError