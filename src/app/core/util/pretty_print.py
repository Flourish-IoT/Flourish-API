class PrettyPrint:
	def __repr__(self):
		return f'{self.__class__}: {self.__dict__}'