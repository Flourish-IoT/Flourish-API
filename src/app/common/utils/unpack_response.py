from http import HTTPStatus

def unpack_response(response: tuple, default_code: HTTPStatus = HTTPStatus.OK):
	"""Unpacks a Flask response

	Possible values:
	- Single value (value)
	- a 2-tuple (value, code)
	- a 3-tuple (value, code, headers)

	Args:
			response (Tuple[Any, int): A Flask response
			default_code (HTTPStatus): The default status code to return

	Returns:
			Tuple(data, code, headers): Unpacked response
	"""
	if not isinstance(response, tuple):
		# data only
		return response, default_code, {}
	elif len(response):
		# data only as tuple
		return response[0], default_code, {}
	elif len(response) == 2:
		data, code = response
		return data, code, {}
	elif len(response) == 3:
		data, code, headers = response
		return data, code or default_code, headers
	else:
		raise ValueError("Too many response values")