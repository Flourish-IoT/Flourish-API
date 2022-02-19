from marshmallow import fields, post_load

from app.core.models.user import User
from app.v1.utils import CamelCaseSchema, DisablePostLoadMixin

class UserSchema(CamelCaseSchema):
	user_id = fields.Int(required=False)
	email = fields.Email(required=True)
	username = fields.Str(required=True)

	@post_load
	def make(self, data, **kwargs):
		return User(**data)

class NewUserSchema(DisablePostLoadMixin, UserSchema):
	password_hash: str = fields.Str(required=True)
	class Meta:
		fields = ("email", "username", "password_hash")