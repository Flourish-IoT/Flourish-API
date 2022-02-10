from marshmallow import fields, post_load

from app.core.models import User
from app.v1.utils import CamelCaseSchema, DisablePostLoadMixin
from .user_preferences_schema import UserPreferencesSchema

class UserSchema(CamelCaseSchema):
	user_id = fields.Int()
	email = fields.Email(required=True)
	username = fields.Str()
	preferences = fields.Nested(UserPreferencesSchema)

	@post_load
	def make(self, data, **kwargs):
		return User(**data)

class NewUserSchema(DisablePostLoadMixin, UserSchema):
	class Meta:
		fields = ('email', )

class UserUpdateSchema(DisablePostLoadMixin, UserSchema):
	class Meta:
		fields = ('email', 'username')
	email = fields.Email(required=False)