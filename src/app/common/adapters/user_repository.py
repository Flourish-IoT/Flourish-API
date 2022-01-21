from abc import ABC
from ..models.users import User
from .sql_alchemy_adapter import SqlAlchemyAdapter

class UserRepositoryABC(ABC):
	pass

class SqlUserRepository(SqlAlchemyAdapter, UserRepositoryABC):
	entity = User
	def __init__(self, session) -> None:
		super().__init__(session)