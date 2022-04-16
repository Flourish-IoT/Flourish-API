from datetime import datetime
import logging
from typing import List
from app.core.errors import NotFoundError, ConflictError
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, exc, update, exists, Integer, Column
import app.core.event_engine.handlers.event_handler as event_handler

import app.core.models.event_engine as models

logger = logging.getLogger(__name__)

def get_event_handler_information(id: int, event_handler_id_column: Column[Integer], session: ScopedSession) -> List[models.EventHandlerInformation]:
	logger.info(f'Getting event handler information for {event_handler_id_column} = {id}')
	query = select(models.EventHandlerInformation).where(event_handler_id_column == id)

	try:
		event_handler_information: List[models.EventHandlerInformation] = session.execute(query).scalars().all()
	except Exception as e:
		logger.error(f'Failed to get event handler information for column {event_handler_id_column} = {id}')
		logger.exception(e)
		raise e

	return event_handler_information

def get_event_handlers(id: int, event_handler_id_column: Column[Integer], session: ScopedSession) -> List[event_handler.EventHandler]:
	logger.info(f'Getting event handlers for {event_handler_id_column} = {id}')
	# TODO: whitelist column?

	# get event handler configs associated with column and ID
	event_handler_information = get_event_handler_information(id, event_handler_id_column, session)

	# get the action configs associated with each event handler
	event_handlers = []
	for handler_info in event_handler_information:
		actions = handler_info.action_information
		if actions is None:
			continue

		# using map of action id to action instance, construct the event handler from the normalized form
		try:
			action_map = {action.action_id: action.to_action() for action in actions}
			event_handlers.append(handler_info.to_event_handler(action_map))
		except Exception as e:
			logger.error('Failed to load action')
			logger.exception(e)

	return event_handlers

def create_event_handler(event_handler: event_handler.EventHandler, session: ScopedSession, *, plant_id: int | None = None, device_id: int | None = None) -> int:
	logger.info(f'Creating {type(event_handler)} EventHandlerInformation with plant_id={plant_id} and device_id={device_id}')

	if plant_id is None and device_id is None:
		raise ValueError('At least one ID is required')

	# Create empty event_handler_information so we can get it's ID
	handler_information = models.EventHandlerInformation(device_id=device_id, plant_id=plant_id)
	actions = event_handler.get_actions()
	action_infos = [models.ActionInformation.from_action(action) for action in actions]
	handler_information.action_information = action_infos

	try:
		session.add(handler_information)
		# flush to get generated ids
		session.flush()
	except exc.DatabaseError as e:
		logger.error('Failed to create Event Handler information')
		logger.exception(e)
		raise e

	# backfill ids for event_handler and actions
	event_handler.event_handler_id = handler_information.event_handler_id
	for action_info in action_infos:
		action_info._action.action_id = action_info.action_id

	# since actions are mutable, they are now populated with action_id and the event handler can now be dumped
	handler_information.update_config(event_handler)

	try:
		session.commit()
	except exc.DatabaseError as e:
		logger.error('Failed to save EventHandlerInformation config, rolling back')
		logger.exception(e)
		session.rollback()
		raise e

	return handler_information.event_handler_id

def delete_event_handler(event_handler_id: int, session: ScopedSession):
	logger.info(f'Deleting event handler {event_handler_id}')
	event_handler = session.get(models.EventHandlerInformation, event_handler_id)
	if event_handler is None:
		raise NotFoundError(f'Could not find event handler with id: {event_handler_id}')

	try:
		session.delete(event_handler)
		session.commit()
	except exc.DatabaseError as e:
		logger.error('Failed to delete event handler')
		logger.exception(e)
		raise e

def update_action_last_executed(action_id: int, last_executed: datetime, session: ScopedSession):
	logger.info(f'Updating action {action_id} last executed time to be {last_executed}')

	try:
		session.execute(
			update(models.ActionInformation)
				.where(models.ActionInformation.action_id == action_id)
				.values(last_executed=last_executed)
		)
		session.commit()
	except exc.NoResultFound as e:
		logger.error('Failed to find action')
		logger.exception(e)
		raise NotFoundError(f'Could not find action with id: {action_id}')
	except exc.DatabaseError as e:
		logger.error('Failed to update action')
		logger.exception(e)
		raise e
