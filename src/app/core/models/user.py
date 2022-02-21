from datetime import datetime
from typing import cast
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

class User(BaseModel):
	__tablename__ = 'users'

	user_id = cast(int, Column(
		Integer,
		primary_key = True
	))

	email = cast(str, Column(
		String()
	))

	username = cast(str, Column(
		String()
	))

	password_hash = cast(str, Column(
		String()
	))

	oauth_token = cast(str, Column(
		String()
	))

	verification_code = cast(int, Column(
		Integer
	))

	password_reset_code = cast(int, Column(
		Integer
	))

	password_reset_code_expiration = cast(datetime, Column(
		TIMESTAMP
	))

	preferences = relationship("UserPreferences", uselist=False, backref='users')