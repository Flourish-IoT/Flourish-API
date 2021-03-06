from base64 import encode
from datetime import datetime, tzinfo
import logging
from typing import List
from app.core.errors import NotFoundError, ConflictError, ForbiddenError
from app.core.models import User, UserPreferences
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import exc, update, select, exists
from app.core.util import emailer, verification
from app.protocols.http.utils import authentication
from app.core.util import authorization
from datetime import datetime, timedelta

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

def create_user(email: str, username: str, password: str, session: ScopedSession):
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
	if email_exists(email, session):
		user_id = _get_user_id(email, session)
		if _is_user_verified(email, session) is False:
			delete_user(user_id, session)
		else:
			return

	code = verification.verify_code()

# unicode string (password) has to be encoded before hash 
	user = User(email=email, password_hash=authorization.hash_password(password.encode('utf-8')), username=username, verification_code=code)

	emailer.send_email(code, "Verification Code for Flourish", email)

	try:
		session.add(user)
		session.commit()
	except exc.IntegrityError as e:
		logging.error('Failed to create user')
		logging.exception(e)
		raise ConflictError('User with email already exists')

	return user.user_id


def login(email: str, password: str, session: ScopedSession) -> str | None :
	"""
	Args:
			email (str): registered user's email ID
			password (str): registered user's password
	"""

	try:
		user: User | None = session.query(User).filter(User.email == email).one_or_none()
		if user is not None:
			if authorization.check_password(password.encode('utf-8'), user.password_hash.encode('utf-8')):
				# Generate JWT
				return authentication.create_jwt(user.username, user.user_id)
		return None
	except Exception as e:
		logging.error(f'Login failed for user {email}')
		logging.exception(e)
		raise e


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

	if not user_exists(user_id, session):
		logging.error('Failed to find user')
		raise NotFoundError(f'Could not find user with ID: {user_id}')

	try:
		session.execute(
			update(User)
				.where(User.user_id == user_id)
				.values(**user_update)
		)
		session.commit()
	except exc.IntegrityError as e:
		logging.error('Failed to update user')
		logging.exception(e)
		raise ConflictError('User with email already exists')
	except exc.DatabaseError as e:
		logging.error('Failed to update user')
		logging.exception(e)
		raise e

	logging.info(f'User {user_id} succesfully updated')

def edit_user_preferences(user_id: int, preferences_update: dict, session: ScopedSession):
	"""Edits user preferences

	Args:
			user_id (int): ID of user being edited
			preferences_update (dict): Updated fields of user preferences. Keys must match field names of UserPreferences
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: User not found
			Exception: Database error
	"""
	logging.info(f'Updating user {user_id} preferences')

	if not user_exists(user_id, session):
		logging.error('Failed to find user')
		raise NotFoundError(f'Could not find user with ID: {user_id}')

	try:
		session.execute(
			update(UserPreferences)
				.where(UserPreferences.user_id == user_id)
				.values(**preferences_update)
		)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to update user preferences')
		logging.exception(e)
		raise e

	logging.info(f'User {user_id} preferences succesfully updated')

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
	user = get_user(user_id, session)

	try:
		session.delete(user)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to delete user')
		logging.exception(e)
		raise e

	# TODO: send email
	# TODO: what to do about devices?

	logging.info(f'User {user_id} succesfully deleted')

def verify_password_reset_code(user_id: int, password_reset_code: str, session: ScopedSession):
	if not user_exists(user_id, session):
		logging.error('Failed to find user')
		raise NotFoundError(f'Could not find user with ID: {user_id}')

	query = select(User.password_reset_code, User.password_reset_code_expiration).where(User.user_id == user_id)
	try:
		result = session.execute(query).one_or_none()
	except exc.DatabaseError as e:
		logging.error('Failed to get user password reset code')
		logging.exception(e)
		raise e

	if result is None or result == (None, None):
		logging.warning(f'User {user_id} does not have reset code')
		return False

	valid_password_reset_code: str | None
	password_reset_code_expiration: datetime | None
	(valid_password_reset_code, password_reset_code_expiration) = result

	# this should never happen
	if valid_password_reset_code is None or password_reset_code_expiration is None:
		logging.error(f'User {user_id} password_reset_code or password_reset_code_expiration is None, ignoring')
		return False

	if password_reset_code_expiration.utcnow() < datetime.utcnow():
		logging.warning(f'Password reset code expired')
		_cleanup_password_reset_code(user_id, session)
		return False

	if password_reset_code != valid_password_reset_code:
		logging.warning(f'Password reset codes do not match')
		return False

	_cleanup_password_reset_code(user_id, session)
	return True

def update_user_password(user_id: int, password: str, new_password: str, session: ScopedSession):
	"""Updates a user's password

	Args:
			user_id (int): ID of user being deleted
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: User not found
			Exception: Database error
	"""
	# TODO: should this log user out?
	logging.info(f'Updating password for user {user_id}')
	_update_password(user_id, new_password, session)
	email = _get_user_email(user_id, session)
	# login(email, new_password, session)

	logging.info(f'Password updated for user {user_id}')

def reset_user_password(user_id: int, reset_code: str, new_password: str, session: ScopedSession):
	"""Resets a user's password

	Args:
			user_id (int): ID of user being deleted
			reset_code (int): User reset code
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: User not found
			ForbiddenError: User does not have permission to reset password
			Exception: Database error
	"""
	logging.info(f'Resetting password for user {user_id}')

	valid = verify_password_reset_code(user_id, reset_code, session)
	if not valid:
		raise ForbiddenError('Invalid password reset code')

	_update_password(user_id, new_password, session)

	try:
		_cleanup_password_reset_code(user_id, session)
	except:
		# ignore failing to cleanup password reset code
		pass

	logging.info(f'Password updated for user {user_id}')

def user_exists(user_id: int, session: ScopedSession) -> bool:
	"""Checks if a user with given user_id exists

	Args:
			user_id (int): User ID to check for
			session (ScopedSession): SQLAlchemy database session

	Returns:
		bool: Represents whether user exists
	"""
	return session.query(exists(User).where(User.user_id == user_id)).scalar()

def email_exists(email: str, session: ScopedSession) -> bool:
	"""Checks if a user with given email exists

	Args:
			email (str): email to check for
			session (ScopedSession): SQLAlchemy database session

	Returns:
		bool: Represents whether user exists
	"""
	return session.query(exists(User).where(User.email == email)).scalar()

def start_user_reset_password(email: str, session: ScopedSession):
	"""Sends user email with authentication code for password reset

	Args:
			email (str): email to check for
			session (ScopedSession): SQLAlchemy database session

	"""
	code = verification.verify_code()
	user =  _get_user_id(email, session)
	if email_exists(email, session):
		emailer.send_email(code, "Flourish Password Reset Code", email)
		_set_password_reset_code(user, code, session)
	else:
		logging.error(f'User does not exist')
		raise NotFoundError(f'Could not find user with email: {email}')

def verify_email_password_reset_code(email: str, code: str, session: ScopedSession):
	"""Verify if user-entered code is same as the code in the database

	Args:
			user_id (int): User ID
			code (int): Verification/Password Reset Code
			session (ScopedSession): Database

	Raises:
			e: _description_
			NotFoundError: _description_

	Returns:
			_type_: _description_
	"""

	user_id = _get_user_id(email, session)
	exists = verify_password_reset_code(user_id, code, session)

	if exists is True:
		return user_id
	else:
		return 0 

def verify_verification_code(email: str, code: str, session: ScopedSession):
	"""Verify if user-entered code is same as the code in the database

	Args:
			user_id (int): User ID
			code (int): Verification/Password Reset Code
			session (ScopedSession): Database

	Raises:
			e: _description_
			NotFoundError: _description_

	Returns:
			_type_: _description_
	"""
	query = select(User).where(User.email == email)

	try:
		result: User = session.execute(query).scalar_one()
	except exc.NoResultFound as e:
		logging.error('Failed to find user')
		logging.exception(e)
		raise NotFoundError(f'Could not find user with the email: {email}')
	except exc.DatabaseError as e:
		logging.error('Failed to get user password reset code')
		logging.exception(e)
		raise e

	if code == result.verification_code:
		_update_user_verification(result.user_id, session)
		return result.user_id
	else:
		return 0


########################################
# INTERNAL USE ONLY
########################################

def _update_password(user_id: int, new_password: str, session: ScopedSession):
	"""
	## [DANGER] INTERNAL USE ONLY
	Updates a user's password.

	Args:
			user_id (int): [description]
			new_password (str): [description]
			session (ScopedSession): [description]

	Raises:
			NotFoundError: [description]
			ConflictError: [description]
			e: [description]
	"""
	new_password_hash = authorization.hash_password(new_password.encode('utf-8'))
	try:
		session.execute(
			update(User)
				.where(User.user_id == user_id)
				.values(password_hash=new_password_hash)
		)
		session.commit()
	except exc.NoResultFound as e:
		logging.error('Failed to find user')
		logging.exception(e)
		raise NotFoundError(f'Could not find user with ID: {user_id}')
	except exc.IntegrityError as e:
		logging.error('Failed to update user password')
		logging.exception(e)
		raise ConflictError(e)
	except exc.DatabaseError as e:
		logging.error('Failed to update user')
		logging.exception(e)
		raise e

def _update_user_verification(user_id: int, session: ScopedSession):
	try:
		session.execute(
		update(User)
			.where(User.user_id == user_id)
			.values(user_verified=True)
		)
		session.commit()
	except exc.NoResultFound as e:
		logging.error('Failed to find user')
		logging.exception(e)
		raise NotFoundError(f'Could not find user with ID: {user_id}')
	except exc.IntegrityError as e:
		logging.error('Failed to update user verification')
		logging.exception(e)
		raise ConflictError(e)
	except exc.DatabaseError as e:
		logging.error('Failed to update user')
		logging.exception(e)
		raise e

def _cleanup_password_reset_code(user_id: int, session: ScopedSession):
	"""
	## [DANGER] INTERNAL USE ONLY
	Cleans up the password_reset_code and password_reset_code_expiration columns

	Args:
			user_id (int): User ID to cleanup
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: User not found
			Exception: Database error
	"""
	try:
		session.execute(
			update(User)
				.where(User.user_id == user_id)
				.values(password_reset_code=None, password_reset_code_expiration=None)
		)
		session.commit()
	except exc.NoResultFound as e:
		logging.error('Failed to find user')
		logging.exception(e)
		raise NotFoundError(f'Could not find user with ID: {user_id}')
	except exc.DatabaseError as e:
		logging.error('Failed to cleanup user password reset code')
		logging.exception(e)
		raise e

def _cleanup_verification_code(user_id: int, session: ScopedSession):
	"""
	## [DANGER] INTERNAL USE ONLY
	Cleans up the password_reset_code and password_reset_code_expiration columns

	Args:
			user_id (int): User ID to cleanup
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: User not found
			Exception: Database error
	"""
	try:
		session.execute(
			update(User)
				.where(User.user_id == user_id)
				.values(verification_code=None)
		)
		session.commit()
	except exc.NoResultFound as e:
		logging.error('Failed to find user')
		logging.exception(e)
		raise NotFoundError(f'Could not find user with ID: {user_id}')
	except exc.DatabaseError as e:
		logging.error('Failed to cleanup user password reset code')
		logging.exception(e)
		raise e

def _set_password_reset_code(user_id: int, code: str, session: ScopedSession):
	"""
	## [DANGER] INTERNAL USE ONLY
	Sets password reset code and the expiration

	Args:
			user_id (int): User ID to cleanup
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: User not found
			Exception: Database error
	"""
	try:
		session.execute(
			update(User)
				.where(User.user_id == user_id)
				.values(password_reset_code=code, password_reset_code_expiration=str(datetime.now() + timedelta(hours=1)))
		)
		session.commit()
	except exc.NoResultFound as e:
		logging.error('Failed to find user')
		logging.exception(e)
		raise NotFoundError(f'Could not find user with ID: {user_id}')
	except exc.DatabaseError as e:
		logging.error('Failed to cleanup user password reset code')
		logging.exception(e)
		raise e

def _set_verification_code(user_id: int, code: str, session: ScopedSession):
	"""
	## [DANGER] INTERNAL USE ONLY
	Replaces the verification code

	Args:
			user_id (int): User ID to cleanup
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: User not found
			Exception: Database error
	"""
	try:
		session.execute(
			update(User)
				.where(User.user_id == user_id)
				.values(verification_code=code)
		)
		session.commit()
	except exc.NoResultFound as e:
		logging.error('Failed to find user')
		logging.exception(e)
		raise NotFoundError(f'Could not find user with ID: {user_id}')
	except exc.DatabaseError as e:
		logging.error('Failed to cleanup user verification code')
		logging.exception(e)
		raise e
	
def _get_user_email(user_id:int, session: ScopedSession):
	"""
	## [DANGER] INTERNAL USE ONLY
	Gets users email address

	Args:
			user_id (int): User ID to cleanup
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: User not found
			Exception: Database error
	"""
	query = select(User).where(User.user_id == user_id)
	try:
		user: User= session.execute(query).scalar_one()
	except exc.NoResultFound as e:
		logging.error('Failed to find user')
		logging.exception(e)
		raise NotFoundError(f'Could not find user with id: {user_id}')
	except Exception as e:
		logging.error(f'Failed to retrieve user')
		logging.exception(e)
		raise e
	
	return user.email

def _get_user_id(email:str, session: ScopedSession):
	query = select(User).where(User.email == email)

	try:
		user: User= session.execute(query).scalar_one()
	except exc.NoResultFound as e:
		logging.error('Failed to find user')
		logging.exception(e)
		raise NotFoundError(f'Could not find user with email: {email}')
	except Exception as e:
		logging.error(f'Failed to retrieve user')
		logging.exception(e)
		raise e

	return user.user_id

def _is_user_verified(email: str, session: ScopedSession):
	"""Verify if user is verified

	Args:
			user_id (int): User ID
			session (ScopedSession): Database

	Raises:
			e: _description_
			NotFoundError: _description_

	Returns:
			_type_: _description_
	"""
	query = select(User).where(User.email == email)

	try:
		result: User = session.execute(query).scalar_one()
	except exc.DatabaseError as e:
		logging.error('Failed to get user password reset code')
		logging.exception(e)
		raise e
	except exc.NoResultFound as e:
		logging.error('Failed to find user')
		logging.exception(e)
		raise NotFoundError(f'Could not find user with the email: {email}')

	if result.user_verified:
		return True
	else:
		return False
	
# TODO: remove this after hunter is done
def _get_users(session: ScopedSession):
	"""Gets all users

	Returns:
			List[User]
	"""
	query = select(User)

	try:
		users: List[User] = session.execute(query).scalars().all()
	except Exception as e:
		logging.error(f'Failed to retrieve users')
		logging.exception(e)
		raise e

	return users
