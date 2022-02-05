from marshmallow import post_load

class DisablePostLoadMixin:
	"""Schema mixin to disable the post_load decorator of subclassed Schemas.

	## MUST BE PASSED BEFORE THE SUBCLASSED SCHEMA

	Example::

		class SchemaExample(DisablePostLoadMixin, BaseSchema):
			...

	Returns:
			[type]: [description]
	"""
	@post_load(pass_original=True)
	def make_user(self, data, original_data, **kwargs):
		return original_data