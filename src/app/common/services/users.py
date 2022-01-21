from app.common.errors.not_found_error import NotFoundError
from app.common.models.users import User

def get_user(user_id: int):
	user = User.query.filter(User.user_id == user_id).first()

	if user is None:
		raise NotFoundError(f'Could not find user with id: {user_id}')

	return user

