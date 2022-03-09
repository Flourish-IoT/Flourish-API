from marshmallow import Schema, fields
import marshmallow.fields as ma_fields

def camelcase(s: str):
	parts = iter(s.split('_'))
	return next(parts) + ''.join(i.title() for i in parts)

class CamelCaseSchema(Schema):
	"""Class that uses camel-case for it's external representation and snake-case for its internal representation"""
	class Meta:
		ordered = True

	def on_bind_field(self, field_name: str, field_obj: ma_fields.Field) -> None:
			field_obj.data_key = camelcase(field_obj.data_key or field_name)
