from copy import deepcopy
from typing import Any
from sqlalchemy.orm.attributes import InstrumentedAttribute

class With:
	"""C# Record Type inspired mixin that changes a property value without mutating the original object"""
	def with_value(self, prop: Any, value: Any):
		"""Returns a new object with updated property value

		Args:
				prop (str | property | sqlalchemy.orm.attributes.InstrumentedAttribute) : Property being modified
				value (Any): New value of property

		Returns:
				Object: New object with updated property value
		"""
		new_copy = deepcopy(self)
		if isinstance(prop, InstrumentedAttribute):
			setattr(new_copy, prop.property.key, value)
		elif isinstance(prop, property):
			if prop.fset is None:
				raise ValueError("Property must have a setter")

			setattr(new_copy, prop.fset.__name__, value)
		else:
			setattr(new_copy, prop, value)

		return new_copy