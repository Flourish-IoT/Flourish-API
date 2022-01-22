from app import db
from .base_model import BaseModel
from flask_restx import fields, Model

UserModel = Model('User', {
	'user_id': fields.Integer,
	'email': fields.String
})

NewUserModel = Model('NewUser', {
	'email': fields.String(required=True),
})

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

	def __init__(self, email:str) -> None:
		super().__init__(email=email) # type: ignore