from flask_restx import fields, Model

UserModel = Model('User', {
	'user_id': fields.Integer,
	'email': fields.String
})

NewUserModel = Model('NewUser', {
	'email': fields.String(required=True),
})
