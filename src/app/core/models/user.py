from datetime import datetime
from typing import cast
from xmlrpc.client import boolean
from .base_model import BaseModel
from . import UserPreferences
from sqlalchemy import Column, Integer, String, TIMESTAMP, Identity, TIME, VARCHAR, Boolean
from sqlalchemy.orm import relationship

class User(BaseModel):
	__tablename__ = 'users'

	user_id = cast(int, Column(
		Integer,
		Identity(True),
		primary_key = True
	))

	email = cast(str, Column(
		String(),
		nullable=False,
		unique=True
	))

	username = cast(str, Column(
		String(),
		nullable=False,
	))

	password_hash = cast(str, Column(
		String(),
		nullable=False
	))

	oauth_token = cast(str, Column(
		String()
	))

	verification_code = cast(str, Column(
		VARCHAR(4)
	))

	password_reset_code = cast(str, Column(
		VARCHAR(4)
	))

	password_reset_code_expiration = cast(datetime, Column(
		TIMESTAMP(True)
	))

	user_verified = cast(bool, Column(
		Boolean(False),
		nullable=False,
		default=False
	))

	preferences = cast(UserPreferences, relationship("UserPreferences", uselist=False, cascade='all', backref='users'))