from random import random
from math import floor


def generate_verification_code() -> str:
	"""
	Generates a string 4 chars long consisting of numbers
	"""
	return "".join(str([floor(random()*10) for i in range(4)]))


def prefix_verification_code(code: str|int) -> str:
	"""
	Prefixes a verification code of less than 4 characters with 0's
	"""
	return (4-len(str(code)))*"0" + str(code)
