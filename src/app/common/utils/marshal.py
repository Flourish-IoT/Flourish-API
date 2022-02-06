from typing import Any, Callable, Type
from marshmallow import Schema
from functools import wraps

from .unpack_response import unpack_response

def marshal(schema: Schema, response: tuple | Any):
	"""Marshals a Flask response using a schema

	Args:
			schema (Schema): Schema to use for marshalling
			response (tuple): Flask response

	Returns:
			tuple | Any: Marshalled response
	"""
	if isinstance(response, tuple):
		data, code, headers = unpack_response(response)
		return schema.dump(data), code, headers

	return schema.dump(response)

def marshal_with(s: Type[Schema]):
	"""A decorator to marshal Flask responses

	Args:
			s (Type[Schema]): Schema model to use during marshaling

	Returns:
			Callable: Decorated function
	"""
	schema = s()

	def decorator(func: Callable):
		@wraps(func)
		def wrapper(*args, **kwargs):
			response = func(*args, **kwargs)
			return marshal(schema, response)
		return wrapper
	return decorator

def marshal_list_with(s: Type[Schema]):
	"""A decorator to marshal list Flask responses

	Args:
			s (Type[Schema]): Schema model to use during marshaling

	Returns:
			Callable: Decorated function
	"""
	schema = s(many=True)

	def decorator(func: Callable):
		@wraps(func)
		def wrapper(*args, **kwargs):
			response = func(*args, **kwargs)
			return marshal(schema, response)
		return wrapper
	return decorator