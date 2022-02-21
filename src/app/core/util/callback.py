from typing import Callable, List, Optional, ParamSpec, TypeVar, Generic

P = ParamSpec("P")
RetT = TypeVar('RetT')

# TODO: return values?
class Callback(Generic[P, RetT]):
	"""
	C# style callbacks

	Inputs:
		P: Callback ParamSpec
		RetT: Callback return value

	Usage::

		def print_int(i: int):
			return print(i)

		def print_int_add_2(i: int):
			return print(i + 2)

		callback = Callback[[int], None]()
		callback.register(print_int)
		callback.register(print_int_add_2)

		callback(2)

	Output::

		2
		4

	"""
	def __init__(self):
		self.listeners: List[Callable[P, RetT | None]] = []

	def register(self, callback: Callable[P, RetT]):
		"""Registers a callback

		Args:
				callback (Callable[P, RetT]): Callback to be registered

		Example::

			def print_int(i: int):
				return print(i)

			callback = Callback[[int], None]()
			callback.register(print_int)

		or::

			...
			callback += print_int


		Returns:
				Callback: Instance of this class, can be used to chain multiple calls together
		"""
		self.listeners.append(callback)
		return self

	def unregister(self, callback: Callable[P, RetT]):
		"""Unregisters a callback

		Args:
				callback (Callable[P, RetT]): Callback to be unregistered

		Example::

			def print_int(i: int):
				return print(i)

			callback = Callback[[int], None]()
			callback.register(int_to_str)
			callback.unregister(int_to_str)

		or::

			...
			callback -= int_to_str


		Returns:
				Callback: Instance of this class, can be used to chain multiple calls together
		"""
		self.listeners.remove(callback)
		return self

	def __iadd__(self, value: Callable[P, RetT]):
		return self.register(value)

	def __isub__(self, value: Callable[P, RetT]):
		return self.unregister(value)

	def __call__(self, *args, **kwargs):
		for listener in self.listeners:
			listener(*args, **kwargs)