from marshmallow import post_load

class DisablePostLoadMixin:
	"""Schema mixin to disable the post_load decorator of subclassed Schemas.

	## MUST BE PASSED BEFORE THE SUBCLASSED SCHEMA
	## `post_load` FUNCTION MUST BE CALLED `make`

	Example::

		class BaseSchema(Schema):
			...
			@post_load
			def make(self, data, **kwargs):
				...

		class SchemaExample(DisablePostLoadMixin, BaseSchema):
			...

	Returns:
			[type]: [description]
	"""
	@post_load
	def make(self, data, **kwargs):
		return data