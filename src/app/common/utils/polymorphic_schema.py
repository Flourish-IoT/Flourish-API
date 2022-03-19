import importlib
import logging
from typing import Any, Optional, Mapping, Type
from marshmallow import fields, ValidationError, Schema

class SchemaField(fields.Field):
	def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
		if value is None:
			raise ValidationError("No schema specified")

		# TODO: make this field type, register type with PolymorphicSchema in dict so we only need class name
		return {
			'__class__': value.__name__,
			'__module__': value.__module__
		}

	def _deserialize(self, value: Any, attr: Optional[str], data: Optional[Mapping[str, Any]], **kwargs):
		if '__class__' not in value or '__module__' not in value:
			raise ValidationError("Invalid schema declaration")

		class_name = value['__class__']
		module_name = value['__module__']

		try:
			# dynamically import module and class
			module = importlib.import_module(module_name)
			schema_class = getattr(module, class_name)
		except Exception as e:
			logging.error(f'Failed to load schema {e}')
			raise ValidationError('Invalid schema')

		return schema_class

class PolymorphicSchema(Schema):
	__schema__ = SchemaField()

class PolymorphicSchemaLoader(Schema):
	"""
	Special kind of schema that allows for polymorphic schemas based on Schema type. Adapted from https://github.com/marshmallow-code/marshmallow-oneofschema
	"""
	__schema__ = SchemaField()

	def load(self, data, *, many=None, partial=None, unknown=None, **kwargs):
		errors = {}
		result_data = []
		result_errors = {}
		many = self.many if many is None else bool(many)
		if partial is None:
			partial = self.partial

		if not many:
			try:
				result = result_data = self._load(data, partial=partial, unknown=unknown, **kwargs)
			except ValidationError as error:
				result_errors = error.normalized_messages()
				result_data.append(error.valid_data)
		else:
			for idx, item in enumerate(data):
				try:
					result = self._load(item, partial=partial, **kwargs)
					result_data.append(result)
				except ValidationError as error:
					result_errors[idx] = error.normalized_messages()
					result_data.append(error.valid_data)

		result = result_data
		errors = result_errors

		if not errors:
			return result

		exception = ValidationError(errors, data=data, valid_data=result)  # type: ignore
		raise exception

	def _load(self, data: dict | Any, *, partial=None, unknown=None, **kwargs):
		if not isinstance(data, dict):
			raise ValidationError({"__schema__": f"Invalid data type: {data}"})

		# get __schema__ field
		if '__schema__' not in data:
			raise ValidationError({'__schema__': 'No schema declared'})

		schema_type = data.pop('__schema__')

		# load schema class
		schema: Type[Schema] | None = self.fields['__schema__'].deserialize(schema_type, '__schema__', data, **kwargs)

		if schema is None:
			raise ValidationError({'__schema__': 'Failed to load schema'})

		# use schema to load data
		s = schema()
		return s.load(data=data, many=False, partial=partial, unknown=unknown, **kwargs)
