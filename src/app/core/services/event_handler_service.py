import logging
from typing import List
from app.core.errors import NotFoundError, ConflictError
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, exc, update, exists, Integer, Column

import app.core.models.event_engine as models
# from app.core.models import ActionInformation, EventHandlerInformation

def get_event_handler_information(id: int, event_handler_id_column: Column[Integer], session: ScopedSession) -> List[models.EventHandlerInformation]:
	logging.info(f'Getting event handler information for {event_handler_id_column} = {id}')
	query = select(models.EventHandlerInformation).where(event_handler_id_column == id)

	try:
		event_handler_information: List[models.EventHandlerInformation] = session.execute(query).scalars().all()
	except Exception as e:
		logging.error(f'Failed to get event handler information for column {event_handler_id_column} = {id}')
		logging.exception(e)
		raise e

	return event_handler_information

def get_event_handler_actions(event_handler_id: int, session: ScopedSession) -> List[models.ActionInformation]:
	# TODO: normalize actions
	logging.info(f'Getting event handler actions for event handler {event_handler_id}')
	query = select(models.ActionInformation).where(models.ActionInformation.event_handler_id == event_handler_id)

	try:
		actions: List[models.ActionInformation] = session.execute(query).scalars().all()
	except Exception as e:
		logging.error(f'Failed to get actions for event handler {event_handler_id}')
		logging.exception(e)
		raise e

	return actions

# def get_event_handler(event_handler_id: int, session: ScopedSession):
# 	event_handler_information = models.EventHandlerInformation()
# 	config = PolymorphicSchema().dump(event_handler)
# 	event_handler_information.config = config
# 	return event_handler_information