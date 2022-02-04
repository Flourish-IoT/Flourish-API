from enum import Enum, IntEnum
from typing import Any, Type
from sqlalchemy import TypeDecorator, Integer

class IntEnumField(TypeDecorator):
	impl = Integer

	def __init__(self, enum_type: Type[IntEnum], *args: Any, **kwargs: Any) -> None:
		super(IntEnumField, self).__init__(*args, **kwargs)
		self._enum_type = enum_type

	def process_bind_param(self, value: IntEnum | int, dialect) -> Any:
			if isinstance(value, Enum):
				return value.value

			return value

	def process_result_value(self, value: int, dialect) -> IntEnum:
			return self._enum_type(value)