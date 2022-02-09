import logging
from typing import List
from app.core.errors import NotFoundError, ConflictError
from app.core.models import Device, Alert, SensorData
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import select, exc, update


def get_alerts(user_id: int, session: ScopedSession, *, viewed: bool | None = None, plant_id: int | None = None, device_id: int | None = None):
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
			[type]: [description]
	"""
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
	alert = session.get(Alert, alert_id)

	if alert is None:
		raise NotFoundError(f'Could not find alert with id: {alert_id}')

	return alert


def create_alert(user_id: int, alert: Alert, session: ScopedSession):
	# TODO:
	raise NotImplementedError()

def delete_alert(alert_id: int, session: ScopedSession):
	"""Deletes alert

	Args:
			alert_id (int): ID of alert being deleted
			session (ScopedSession): SQLAlchemy database session

	Raises:
			NotFoundError: Device not found
			Exception: Database error
	"""
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