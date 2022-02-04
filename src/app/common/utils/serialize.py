from enum import Enum
import logging
from werkzeug.exceptions import BadRequest
from typing import Callable, Type
from marshmallow import Schema, ValidationError, INCLUDE, RAISE
from functools import wraps
from flask import request

class Location(Enum):
	BODY = "body"
	QUERY_PARAMETER = "query"
	FORM = "form"
	# TODO: headers, path, cookies, files?

def serialize(schema: Schema, *, location: Location = Location.BODY):
	"""Serializes and validates request data.

	Args:
			schema (Schema): Schema used for serialization
			location (Location, optional): Location of data being serialized. Defaults to Location.BODY.

	Raises:
			BadRequest: Validation errors occured

	Returns:
			Type[Schema]: Serialized response
	"""
	# get data from the json body
	if location == Location.BODY:
		data = request.get_json()
		if data is None:
			raise BadRequest

	# get data from query parameters
	elif location == Location.QUERY_PARAMETER:
		data = request.args

	# get data from form data
	elif location == Location.FORM:
		data = request.form

	try:
		d = schema.load(data)
	except ValidationError as e:
		logging.warn('Failed to validate input:')
		logging.warn(e.messages)
		raise BadRequest(e.messages)

	return d

def serialize_with(s: Type[Schema], *, location: Location = Location.BODY, strict: bool = True, raise_on_validation_error: bool = True):
	"""Validates and serializes request data. Serialized data is automatically injected into the arguments of the method being decorated

	Injected argument is based off of location:
	- Location.BODY - `body`
	- Location.QUERY_PARAMETER - `query`
	- Location.FORM - `form`

	Args:
			s (Type[Schema]): Schema used for serialization
			location (Location, optional): Location of data being serialized. Defaults to Location.BODY.
			strict (bool, optional): Controls strictness of validation. If `True`, validation errors will be raised on unknown fields. Defaults to True.
			raise_on_validation_error (bool, optional): Raise a 400 BadRequest exception on validation error. Defaults to True.

	Raises:
			BadRequest: Validation errors occured

	Returns:
			Callable: Decorated function
	"""
	schema = s(unknown=RAISE if strict else INCLUDE)

	def decorator(func: Callable):
		@wraps(func)
		def wrapper(*args, **kwargs):
			try:
				data = serialize(schema, location=location)
			except BadRequest as e:
				if raise_on_validation_error:
					raise e

				data = None

			# inject parsed request into function
			return func(*args, **{ location.value: data }, **kwargs)

		return wrapper
	return decorator