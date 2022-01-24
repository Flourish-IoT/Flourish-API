from .base_model import BaseModel
from sqlalchemy import Column, Integer, String

class User(BaseModel):
	__tablename__ = 'users'

	user_id = Column(
		Integer,
		primary_key = True
	)
	email = Column(
		String(),
		nullable=False
	)