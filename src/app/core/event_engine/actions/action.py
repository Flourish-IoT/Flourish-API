from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any

class Action(ABC):
	cooldown: timedelta
	disabled: bool

	def __init__(self, disabled: bool, cooldown: timedelta):
		self.disabled = disabled
		self.cooldown = cooldown

	def can_execute(self):
		if self.disabled:
			return False

		# TODO: check if on cooldown
		pass

	@abstractmethod
	def execute(self) -> bool:
		pass