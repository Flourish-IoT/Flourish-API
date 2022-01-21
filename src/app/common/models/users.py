from ... import db
from flask_sqlalchemy.model import DefaultMeta
from .base_model import BaseModel

class User(BaseModel):
	__tablename__ = 'users'

	user_id = db.Column(
		db.Integer,
		primary_key = True
	)
	email = db.Column(
		db.String(),
		nullable=False
	)