import logging
from app.core.errors import NotFoundError, ConflictError
from app.core.models import User
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import exc, update

def get_user(user_id: int, session: ScopedSession):
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
		raise NotFoundError(f'Could not find user with ID: {user_id}')

	return user

def create_user(email: str, session: ScopedSession):
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

def edit_user(user_id: int, user_update: dict, session: ScopedSession):
	"""Edits user information

	Args:
			user_id (int): ID of user being edited
			user_update (dict): Updated fields of user. Keys must match field names of User
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: User not found
			Exception: Database error
	"""
	logging.info(f'Updating user {user_id}')

	try:
		session.execute(
			update(User)
				.where(User.user_id == user_id)
				.values(**user_update)
		)
		session.commit()
	except exc.NoResultFound as e:
		logging.error('Failed to find user')
		logging.exception(e)
		raise NotFoundError(f'Could not find user with ID: {user_id}')
	except exc.IntegrityError as e:
		logging.error('Failed to update user')
		logging.exception(e)
		raise ConflictError('User with email already exists')
	except exc.DatabaseError as e:
		logging.error('Failed to update user')
		logging.exception(e)
		raise e

	logging.info(f'User {user_id} succesfully updated')

def delete_user(user_id: int, session: ScopedSession):
	"""Deletes user and sends them an email

	Args:
			user_id (int): ID of user being deleted
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: User not found
			Exception: Database error
	"""
	logging.info(f'Deleting user {user_id}')
	device = get_user(user_id, session)

	try:
		session.delete(device)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to delete user')
		logging.exception(e)
		raise e

	# TODO: send email
	# TODO: what to do about devices?

	logging.info(f'User {user_id} succesfully deleted')