import logging
from typing import List
from app.core.errors import NotFoundError, ConflictError
from app.core.models import Alert, Plant, ValueRating, SeverityLevelEnum
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, exc, update
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

def get_alerts(user_id: int, session: ScopedSession, *, viewed: bool | None = None, plant_id: int | None = None, device_id: int | None = None) -> List[Alert]:
	"""Gets all alerts for a user

	Args:
			user_id (int): ID of user
			session (ScopedSession): SQLALchemy database session
			viewed (bool, optional): Filter by viewed status. Defaults to None.
			device_id (int, optional): ID of device to filter by. Defaults to None.
			plant_id (int, optional): ID of plant to filter by. Defaults to None.

	Raises:
			ValueError: Cannot pass both plant_id and device_id
			Exception: Failed to get alerts

	Returns:
			List[Alert]: Alerts
	"""
	logger.info(f'Getting alerts for user {user_id} with filters (viewed={viewed}, plant_id={plant_id}, device_id={device_id}')
	if plant_id is not None and device_id is not None:
		raise ValueError('Cannot pass both plant_id and device_id')

	query = select(Alert).where(Alert.user_id == user_id)

	if viewed is not None:
		query = query.where(Alert.viewed == viewed)

	if plant_id is not None:
		query = query.where(Alert.plant_id == plant_id)

	if device_id is not None:
		query = query.where(Alert.device_id == device_id)

	try:
		alerts: List[Alert] = session.execute(query).scalars().all()
	except Exception as e:
		logging.error(f'Failed to get alerts for user {user_id}')
		logging.exception(e)
		raise e

	logger.debug(f'Found {len(alerts)} alerts')
	return alerts

def get_alert(alert_id: int, session: ScopedSession):
	"""Gets a alert by alert ID

	Args:
			alert_id (int): ID of the alert

	Raises:
			NotFoundError: Alert not found

	Returns:
			Alert
	"""
	logger.debug(f'Getting alert {alert_id}')
	alert = session.get(Alert, alert_id)

	if alert is None:
		raise NotFoundError(f'Could not find alert with id: {alert_id}')

	return alert


def create_alert(user_id: int, alert: Alert, session: ScopedSession) -> int:
	"""Creates alert

	Args:
			user_id (int): ID of user
			alert (Alert): Alert to be created
			session (ScopedSession): SQLAlchemy database session

	Raises:
			ConflictError: _description_

	Returns:
			int: Alert ID
	"""
	logger.info(f'Creating new alert for user {user_id}')
	logger.debug(f'Alert: {alert}')
	alert.user_id = user_id

	try:
		session.add(alert)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to create alert')
		logging.exception(e)
		raise e

	# TODO: push notifications
	logger.info(f'Alert {alert.alert_id} created')
	return alert.alert_id

def delete_alert(alert_id: int, session: ScopedSession):
	"""Deletes alert

	Args:
			alert_id (int): ID of alert being deleted
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: Device not found
			Exception: Database error
	"""
	logger.info(f'Deleting alert {alert_id}')
	alert = get_alert(alert_id, session)

	try:
		session.delete(alert)
		session.commit()
	except exc.DatabaseError as e:
		logging.error('Failed to delete alert')
		logging.exception(e)
		raise e

def set_viewed_state(alert_ids: List[int], viewed: bool, session: ScopedSession):
	"""Sets the viewed state for multiple alerts

	Args:
			alert_ids (List[int]): List of alert IDs
			viewed (bool): Value to set the viewed state
			session (ScopedSession): SQLAlchemy database session

	Raises:
			Exception: Database error
	"""
	logger.info(f'Setting viewed state for alerts {alert_ids} to {viewed}')
	try:
		session.execute(
			update(Alert)
				.filter(Alert.alert_id.in_(alert_ids)) # type: ignore
				.values(viewed=viewed)
		)
		session.commit()
	except Exception as e:
		logging.error(f'Failed to get alerts to set viewed state. Alert IDs: {alert_ids}')
		logging.exception(e)
		raise e