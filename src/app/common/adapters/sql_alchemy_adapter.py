from typing import Any
from .abstract_adapter import AbstractAdapter
from sqlalchemy.orm import Session

class SqlAlchemyAdapter(AbstractAdapter):
	entity = NotImplementedError

	def __init__(self, session: Session) -> None:
		self.session = session

	def add(self, item: Any):
		self.session.add(item)

	def get_by_id(self, id: int):
		return self.session.query(self.entity).get(id)

