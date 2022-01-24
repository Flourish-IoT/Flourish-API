class ConflictError(Exception):
	def __init__(self, message='Resource already exists', *args: object) -> None:
			super().__init__(message, *args)