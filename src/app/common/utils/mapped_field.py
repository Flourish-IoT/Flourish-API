from typing import Any, Callable, Dict, Generic, Type, TypeVar
from marshmallow import ValidationError
from marshmallow.fields import Field

T = TypeVar('T')
class MappedField(Field, Generic[T]):
	def __init__(self, context_key: str, mapping_func: Callable[[T], Any] = lambda x: x, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.context_key = context_key
		self.mapping_func = mapping_func

	def _serialize(self, value, attr, obj, **kwargs) -> None:
		# apply mapping func to get key
		return self.mapping_func(value)

	def _deserialize(self, value, attr, data, **kwargs) -> None:
		# get schema context and use it to map from key back to value
		if self.context_key not in self.context:
			raise ValidationError(f'Context key {self.context_key} does not exist')

		context: Dict = self.context[self.context_key]
		if value not in context:
			raise ValidationError(f'No mapping for {value}')

		return context[value]