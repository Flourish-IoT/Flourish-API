import logging
from typing import Any, Dict

from app.common.schemas import SQLAlchemyColumnField, SerializableClass, DynamicField
from app.core.event_engine.events import Event

from .queries import Query
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy import Column

from marshmallow import Schema, fields, post_load

#######################
# Schemas
#######################
class FieldSchema(Schema):
	field = SQLAlchemyColumnField()
	queries = fields.Dict(keys=fields.String(), values=DynamicField([Query]))

	@post_load
	def make(self, data, **kwargs):
		return Field(**data)
#######################

# TODO: this probably doesn't even need to exist, can be replaced by passing col into Query
class Field(SerializableClass):
	__schema__ = FieldSchema

	field: Column
	queries: Dict[str, Query]

	def __init__(self, field: Column | Any, queries: Dict[str, Query]) -> None:
		self.field = field
		self.queries = queries

	def get_value(self, id: int, session: ScopedSession, event: Event):
		logging.info(f'Getting value for field {self.field} and id {id}')
		value = {}
		for field, query in self.queries.items():
			value[field] = query.execute(id, self.field, session, event)

		logging.info(f'Value={value}')
		return value