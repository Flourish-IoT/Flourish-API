import abc


class AbstractUnitOfWork(abc.ABC):
	@abc.abstractmethod
	def commit(self):
		raise NotImplementedError

	@abc.abstractmethod
	def rollback(self):
		raise NotImplementedError

	def __exit__(self, *args):
		self.rollback()