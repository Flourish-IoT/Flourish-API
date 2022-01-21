from ..models.users import User

def get_user(user_id: int):
	user = User.query.filter(User.user_id == user_id).first()

	if user is None:
		raise Exception(f'Cannot find user with id {user_id}')

	return user

