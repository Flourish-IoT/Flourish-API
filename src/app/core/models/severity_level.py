from enum import IntEnum
from .base_model import BaseModel
from sqlalchemy import Column, Integer, String

class SeverityLevel(BaseModel):
	__tablename__ = 'severity_levels'

	severity_id = Column(
		Integer,
		primary_key = True
	)
	description = Column(
		String(),
		nullable=False
	)

class SeverityLevelEnum(IntEnum):
	Info = 1,
	Warning = 2,
	Critical = 3,
	Error = 4,

	@classmethod
	def get_severity_levels(cls):
		"""
		Returns all valid severity levels
		"""
		return [e.name for e in cls]