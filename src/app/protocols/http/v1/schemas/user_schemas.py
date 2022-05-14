from enum import Enum
from typing_extensions import Required
from marshmallow import Schema, fields, post_load, validates_schema, ValidationError
from marshmallow_enum import EnumField

from app.core.models import User
from app.core.util import verification
from app.protocols.http.utils import CamelCaseSchema, DisablePostLoadMixin
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
		password = fields.Str()
		class Meta:
			fields = ('email', 'username', 'password')

class UserUpdateSchema(DisablePostLoadMixin, UserSchema):
    class Meta:
        fields = ('email', 'username')
    email = fields.Email(required=False)

class ResetUserPasswordSchema(DisablePostLoadMixin, UserSchema):
    class Meta:
        fields = ('email', )

class AuthenticationType(Enum):
    password = 1,
    reset_code = 2

class UserPasswordUpdateSchema(CamelCaseSchema):
    authentication_type = EnumField(AuthenticationType, required = True)
    authentication = fields.Raw(required=True)
    new_password = fields.Str(required=True)

    @validates_schema
    def validate_authentication(self, data, **kwargs):
        auth = data['authentication']

        # if using password authentication, authentication field must be a string
        if data['authentication_type'] == AuthenticationType.password:
            if type(auth) != str:
                raise ValidationError('Not a valid string', field_name='authentication')
        else:
        # if using password reset code authentication, authentication field must be an int
            if type(auth) != str:
                raise ValidationError('Not a valid string', field_name='authentication')

class LoginSchema(CamelCaseSchema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class VerificationCodeType(Enum):   
    verification = 1,
    password_reset = 2

class VerifyQueryParameterSchema(Schema):
    code_type = EnumField(VerificationCodeType, required=True)

class VerifySchema(CamelCaseSchema):
    email = fields.Email(required=True)
    code = fields.Str(required=True)

# TODO: REMOVE THIS WHEN HUNTER IS DONE
class UserSummarySchema(UserSchema):
    class Meta:
        fields = ('email', 'username')
