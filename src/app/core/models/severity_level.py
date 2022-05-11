from enum import IntEnum

from app.core.util import EnumValuesMixin
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String, Identity

class SeverityLevel(BaseModel):
	__tablename__ = 'severity_levels'

	severity_id = Column(
		Integer,
		Identity(True),
		primary_key = True
	)
	description = Column(
		String(),
		nullable=False
	)

class SeverityLevelEnum(EnumValuesMixin, IntEnum):
	Info = 1,
	Warning = 2,
	Critical = 3,
	Error = 4,