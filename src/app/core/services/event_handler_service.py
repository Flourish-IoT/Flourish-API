from __future__ import annotations

from datetime import datetime
from typing import List
from app.core.errors import NotFoundError, ConflictError
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, exc, update, exists, Integer, Column
import app.core.event_engine.handlers.event_handler as event_handler
import app.core.models.event_engine as models

import logging
logger = logging.getLogger(__name__)

# TODO: whitelist column?
def get_event_handler_information(id: int, event_handler_id_column: Column[Integer], session: ScopedSession) -> List[models.EventHandlerInformation]:
	"""Returns the raw EventHandlerInformation for all event handlers matching the ID using the given column

	Args:
			id (int): ID to match on
			event_handler_id_column (Column[Integer]): Column to use in where query. Can be alert_id or device_id
			session (ScopedSession): SQLALchemy database session

	Raises:
			e: Failed to get event handler information

	Returns:
			List[models.EventHandlerInformation]
	"""
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
	"""Returns fully hydrated event handlers for all event handlers matching the ID using the given column

	Args:
			id (int): ID to match on
			event_handler_id_column (Column[Integer]): Column to use in where query. Can be alert_id or device_id
			session (ScopedSession): SQLALchemy database session

	Returns:
			List[event_handler.EventHandler]
	"""
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

def create_event_handler(event_handler: event_handler.EventHandler, session: ScopedSession, *, plant_id: int | None = None, device_id: int | None = None, auto_commit: bool =True) -> int:
	"""Registers a new event handler and it's actions

	Args:
			event_handler (event_handler.EventHandler): Event handler to register
			session (ScopedSession): SQLALchemy database session
			plant_id (int | None, optional): ID of the plant to associate with the event handler. Defaults to None.
			device_id (int | None, optional): ID of the device to associate with the event handler. Defaults to None.
			auto_commit (bool, optional): Whether or not to commit changes to the database. Defaults to True.

	Raises:
			ValueError: No IDs passed
			e: Failed to create EventHandlerInformation
			e: Failed to save EventHandlerInformation config

	Returns:
			int: ID of newly created event handler
	"""
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

	logger.info(f'Event handler flushed, backfilling IDs and saving config')
	# backfill ids for event_handler and actions
	event_handler.event_handler_id = handler_information.event_handler_id
	for action_info in action_infos:
		action_info._action.action_id = action_info.action_id

	# since actions are mutable, they are now populated with action_id and the event handler can now be dumped
	handler_information.update_config(event_handler)

	try:
		if auto_commit:
			session.commit()
	except exc.DatabaseError as e:
		logger.error('Failed to save EventHandlerInformation config, rolling back')
		logger.exception(e)
		session.rollback()
		raise e

	logger.info(f'Event handler {handler_information.event_handler_id} created')
	return handler_information.event_handler_id

def delete_event_handler(event_handler_id: int, session: ScopedSession):
	"""Deletes an event handler and it's actions

	Args:
			event_handler_id (int): ID of event handler to delete
			session (ScopedSession): SQLALchemy database session

	Raises:
			NotFoundError: Could not find event handler
			e: Failed to delete event handler
	"""
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
	"""Updates Action last_executed time

	Args:
			action_id (int): Action being updated
			last_executed (datetime): New last_executed time
			session (ScopedSession): SQLALchemy database session

	Raises:
			NotFoundError: Failed to find action
			e: Failed to update action
	"""
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
