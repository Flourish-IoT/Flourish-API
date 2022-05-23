from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypeVar

from app.common.schemas import DynamicField

from . import ActionSchema, Action
from app.core.event_engine.events import Event

import requests
import ast

from marshmallow import fields, post_load, INCLUDE
from marshmallow_enum import EnumField

import logging
logger = logging.getLogger(__name__)

Headers = Dict[str, str]
Body = str | Dict[str, Any] | List[tuple[str, str | None]]
Params = Dict[str, str]

#######################
# Schemas
#######################
class HTTPActionSchema(ActionSchema):
	method = fields.Str()
	url = fields.Str()

	body = DynamicField([str, dict, list], allow_none=True)
	params = DynamicField([dict], allow_none=True)
	headers = DynamicField([dict], allow_none=True)

	@post_load
	def make(self, data, **kwargs):
		return HTTPAction(**data)
#######################

class HTTPAction(Action):
	__schema__ = HTTPActionSchema

	method: str
	url: str

	body: Body | None
	params: Params | None
	headers: Headers | None

	def __init__(self, url: str, method: str, body: Optional[Body] = None, params: Optional[Params] = None, headers: Optional[Headers] = None, disabled: bool = False, action_id: Optional[int] = None, cooldown: Optional[timedelta] = None, last_executed: Optional[datetime] = None):
		self.url = url
		self.method = method
		self.body = body
		self.params = params
		self.headers = headers
		super().__init__(disabled, action_id=action_id, cooldown=cooldown, last_executed=last_executed)

	# TODO: this can be improved a lot, doesnt work for classes. Serialize them?
	def format_value(self, value: Any, event: Event) -> Any:
		v = value.format(event=event)
		# try parsing it as a literal so we can get native datatypes
		try:
			return ast.literal_eval(v)
		except Exception:
			return v

	T = TypeVar('T', bound = Dict[str, Any] | str | List[Any] | None)
	def template(self, value: T, event: Event) -> T:
		"""Recursively templates each string

		Args:
				value (Dict[str, Any] | str | List[Any] | None): Value to be templated
				event (Event): Event to use for template

		Returns:
				T: Templated values
		"""
		match value:
			case str():
				return self.format_value(value, event)
				# return value.format(event=event)
			case dict():
				for key, val in value.items():
					value[key] = self.template(val, event)
			case list():
				for i, val in enumerate( value ):
					value[i] = self.template(val, event)

		return value

	def execute(self, event: Event) -> bool:
		logger.info('Executing HTTPAction')

		if not self.can_execute():
			return False

		self.url = self.template(self.url, event)
		self.body = self.template(self.body, event)
		self.params = self.template(self.params, event)
		self.headers = self.template(self.headers, event)

		# TODO: allow users to pass requests? chain actions like action.onSuccess or action.onError?
		# TODO: Auth?
		try:
			response = requests.request(method=self.method, url=self.url, params=self.params, json=self.body, headers=self.headers, timeout=10)
		except requests.RequestException as e:
			logger.error(f'Request failed: {e}')
			logger.exception(e)
			return False

		# update last executed time
		self.update_last_executed(event)

		return response.ok
