from datetime import datetime
from typing import cast

from .base_model import BaseModel
from .severity_level import SeverityLevelEnum
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean, Identity, text
from sqlalchemy.sql import func
from .int_enum_field import IntEnumField

class Alert(BaseModel):
	__tablename__ = 'alerts'

	alert_id = cast(int, Column(
		Integer,
		Identity(True),
		primary_key = True,
	))

	plant_id = cast(int, Column(
		Integer,
		ForeignKey('plants.plant_id', ondelete='CASCADE'),
	))

	device_id = cast(int, Column(
		Integer,
		ForeignKey('devices.device_id', ondelete='CASCADE'),
	))

	user_id = cast(int, Column(
		Integer,
		ForeignKey('users.user_id', ondelete='CASCADE'),
	))

	action_id = cast(int, Column(
		Integer,
		ForeignKey('actions.action_id', ondelete='SET NULL'),
	))

	severity = cast(SeverityLevelEnum, Column(
		'severity_id',
		IntEnumField(SeverityLevelEnum),
		ForeignKey('severity_levels.severity_id')
	))

	message = cast(str, Column(
		String,
		nullable=False
	))

	time = cast(datetime, Column(
		TIMESTAMP(True),
		server_default=func.now()
	))

	viewed = cast(bool, Column(
		Boolean,
		server_default=text('FALSE'),
		nullable=False
	))