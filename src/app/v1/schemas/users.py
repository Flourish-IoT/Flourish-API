from marshmallow import fields
from .camel_case_schema import CamelCaseSchema

class UserSchema(CamelCaseSchema):
	user_id = fields.Int()
	email = fields.Email(required=True)

class NewUserSchema(UserSchema):
	class Meta:
		fields = ('email', )