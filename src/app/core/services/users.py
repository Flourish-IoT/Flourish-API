from app.core.errors import NotFoundError, ConflictError
from app.core.models import User
from sqlalchemy.orm.session import Session
from sqlalchemy import exc
import logging

def get_user(user_id: int, session: Session):
	"""Gets a user by user ID

	Args:
			user_id (int): [description]

	Raises:
			NotFoundError: User not found

	Returns:
			User: [description]
	"""
	user = session.get(User, user_id)

	if user is None:
		raise NotFoundError(f'Could not find user with id: {user_id}')

	return user

def create_user(email: str, session: Session):
	"""Creates a new user

	Args:
			email (str): [description]
			session (Session): [description]

	Raises:
			ConflictError: User already exists
			Exception: A database exception has occured

	Returns:
			int: Newly created user ID
	"""
	# TODO: this needs to be expanded
	user = User(email=email)

	try:
		session.add(user)
		session.commit()
	except exc.IntegrityError as e:
		logging.error('Failed to create user')
		logging.exception(e)
		raise ConflictError('User with email already exists')

	return user.user_id