from datetime import datetime
from typing import cast

from .base_model import BaseModel
from .severity_level import SeverityLevelEnum
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import INET
from .int_enum_field import IntEnumField

class Alert(BaseModel):
	__tablename__ = 'alerts'

	alert_id = cast(int, Column(
		Integer,
		primary_key = True
	))

	plant_id = cast(int, Column(
		Integer,
		ForeignKey('plant_id.plant_id'),
	))

	device_id = cast(int, Column(
		Integer,
		ForeignKey('device_id.device_id'),
	))

	user_id = cast(int, Column(
		Integer,
		ForeignKey('user_id.user_id'),
	))

	severity = cast(SeverityLevelEnum, Column(
		'severity_id',
		IntEnumField(SeverityLevelEnum),
		ForeignKey('severity_levels.severity_id')
	))

	message = cast(str, Column(
		String,
	))

	time = cast(datetime, Column(
		TIMESTAMP,
	))

	viewed = cast(bool, Column(
		Boolean,
	))