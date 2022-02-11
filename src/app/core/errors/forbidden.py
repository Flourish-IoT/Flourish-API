class ForbiddenError(Exception):
	def __init__(self, message='Request forbidden', *args: object) -> None:
			super().__init__(message, *args)
