from datetime import datetime
from typing import cast
from ..base_model import BaseModel
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type

class EventHandlerInformation(BaseModel):
	__tablename__ = 'event_handlers'

	event_handler_id = cast(int, Column(
		Integer,
		primary_key = True
	))

	plant_id = cast(int | None, Column(
		Integer,
		ForeignKey('plants.plant_id'),
	))

	device_id = cast(int | None, Column(
		Integer,
		ForeignKey('devices.device_id'),
	))

	config = Column(
		mutable_json_type(dbtype=JSONB, nested=True),
		nullable=False
	)