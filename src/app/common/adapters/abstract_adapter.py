import abc

class AbstractAdapter(abc.ABC):
	@abc.abstractmethod
	def add(self, item):
		raise NotImplementedError

	@abc.abstractmethod
	def get_by_id(self, id):
		raise NotImplementedError