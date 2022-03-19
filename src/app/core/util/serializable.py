from abc import ABC
import importlib
import logging
from typing import Any, Mapping, Optional, Type
from marshmallow import Schema, fields, ValidationError, pre_load

class Serializable(ABC):
	__schema__: Type[Schema] | None

	@classmethod
	def serialize(cls, data, **kwargs):
		if cls.__schema__ is None:
			raise ValueError("Schema must be defined")

		schema = cls.__schema__(**kwargs)
		return schema.load(data)

	def marshal(self, **kwargs):
		if self.__schema__ is None:
			raise ValueError("Schema must be defined")

		schema = self.__schema__(**kwargs)
		return schema.dump(self)
