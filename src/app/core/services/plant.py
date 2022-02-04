from select import select

from flask import session
from app.core.errors import NotFoundError, ConflictError
from app.core.models import User
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import exc, select
from typing import List
import logging

from app.core.models.plant import Plant

def get_plants(user_id: int, session: ScopedSession):
	query = select(Plant).where(Plant.user_id == user_id)

	try:
		plants: List[Plant] = session.execute(query).scalars().all()
	except Exception as e:
		logging.error(f'Failed to get plants for user')
		logging.exception(e)
		raise e

	return plants