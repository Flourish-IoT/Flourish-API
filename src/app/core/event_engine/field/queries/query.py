from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Type
from app.core.models import BaseModel, SensorData
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import Column, TIMESTAMP, Integer

whitelisted_tables = [SensorData]
class Query(ABC):
	column: Column
	time_column: Column[TIMESTAMP]
	id_column: Column[Integer]
	table: BaseModel

	def __init__(self, table: BaseModel, id_column: Column[Integer], time_column: Column[TIMESTAMP], column: Column):
		if table not in whitelisted_tables:
			raise ValueError(f'Table {table} is restricted')
		self.column = column
		self.time_column = time_column
		self.id_column = id_column
		self.table = table

	@abstractmethod
	def execute(self, id: int, session: ScopedSession) -> Any:
		raise NotImplementedError