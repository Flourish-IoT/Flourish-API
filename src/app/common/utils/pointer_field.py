from typing import Any, Type
from marshmallow import fields, ValidationError

class PointerField(fields.Field):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

	def _serialize(self, value, attr, obj, **kwargs) -> None:
		pass

	def _deserialize(self, value, attr, data, **kwargs) -> None:
		pass