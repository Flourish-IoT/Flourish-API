from typing import cast
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String

class User(BaseModel):
	__tablename__ = 'users'

	user_id = cast(int, Column(
		Integer,
		primary_key = True
	))
	email = cast(str, Column(
		String(),
		nullable=False
	))
	username = cast(str, Column(
		String(),
		nullable=False
	))
	password_hash = cast(str, Column(
		String(),
		nullable=False
	))